import asyncio
import threading
import time
import math
import os
import platform
import pandas as pd
import numpy as np
from typing import Dict, Any, List

# Try to import scapy, but handle absence gracefully
try:
    import scapy.all as scapy
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

from backend.services.inference_service import inference_service

class LiveCaptureService:
    def __init__(self):
        self.is_capturing = False
        self.capture_thread = None
        self.interface = None
        self.status = "STOPPED"
        self.temporal_buffer = [] # list of 55-feature dicts
        self.error_message = None
        
        self.subscribers = set()
        
        # Determine feature columns from demo data to match exactly
        try:
            demo_df = inference_service.get_demo_data()
            meta_cols = ['window_start', 'window_end', 'attack_binary', 'attack_type', 'attack_family', 'ground_truth_source', 'label_confidence', 'label']
            self.feature_cols = [c for c in demo_df.columns if c not in meta_cols]
        except:
            self.feature_cols = [f"Feature_{i}" for i in range(55)]
            
    def check_npcap(self) -> bool:
        if platform.system() == "Windows":
            # Check common Npcap/WinPcap installation paths
            npcap_path = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "System32", "Npcap", "wpcap.dll")
            winpcap_path = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "System32", "wpcap.dll")
            return os.path.exists(npcap_path) or os.path.exists(winpcap_path)
        return True

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "interface": self.interface,
            "temporal_states": len(self.temporal_buffer),
            "error": self.error_message,
            "npcap_installed": self.check_npcap(),
            "scapy_available": SCAPY_AVAILABLE
        }

    def start_capture(self, interface: str):
        if self.is_capturing:
            raise RuntimeError("Capture is already running.")
            
        if not SCAPY_AVAILABLE:
            self.status = "ERROR"
            self.error_message = "Scapy is not installed. Please install scapy."
            raise RuntimeError(self.error_message)
            
        if not self.check_npcap():
            self.status = "ERROR"
            self.error_message = "Npcap is not installed. Please install Npcap for Windows packet capture."
            raise RuntimeError(self.error_message)
            
        self.interface = interface
        self.is_capturing = True
        self.status = "CAPTURING"
        self.error_message = None
        self.temporal_buffer = []
        
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
    def stop_capture(self):
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        self.status = "STOPPED"

    def broadcast_sync(self, message: Dict[str, Any]):
        disconnected = set()
        for q in self.subscribers:
            try:
                q.put_nowait(message)
            except:
                disconnected.add(q)
        self.subscribers -= disconnected

    def _capture_loop(self):
        try:
            while self.is_capturing:
                start_time = time.time()
                
                # Sniff for 5 seconds
                packets = scapy.sniff(iface=self.interface, timeout=5.0)
                
                if not self.is_capturing:
                    break
                    
                if len(packets) < 2:
                    # Not enough traffic
                    self.broadcast_sync({"type": "info", "message": "Insufficient traffic for valid state"})
                    continue
                    
                state = self._extract_features(packets, start_time)
                self.temporal_buffer.append(state)
                
                if len(self.temporal_buffer) > 10:
                    self.temporal_buffer.pop(0)
                    
                if len(self.temporal_buffer) < 10:
                    self.status = "BUILDING CONTEXT"
                    self.broadcast_sync({
                        "type": "building_context", 
                        "states": len(self.temporal_buffer)
                    })
                    continue
                    
                self.status = "PREDICTING"
                
                # Run inference
                try:
                    # Build DataFrame
                    df_data = []
                    for i, st in enumerate(self.temporal_buffer):
                        # Construct exact features
                        row = {"window_start": start_time - (9-i)*5.0} # Ensure perfect 5s gaps
                        for col in self.feature_cols:
                            row[col] = st.get(col, 0.0)
                        df_data.append(row)
                        
                    df = pd.DataFrame(df_data)
                    
                    if inference_service.engine:
                        result = inference_service.analyze(df, k=3)
                        
                        # Calculate live evidence
                        src_ips = set()
                        dst_ips = set()
                        dst_ports = set()
                        flags_dist = {"SYN": 0, "ACK": 0, "FIN": 0, "RST": 0}
                        
                        for p in packets:
                            if scapy.IP in p:
                                src_ips.add(p[scapy.IP].src)
                                dst_ips.add(p[scapy.IP].dst)
                            if scapy.TCP in p:
                                dst_ports.add(p[scapy.TCP].dport)
                                flags = p[scapy.TCP].flags
                                if 'S' in flags: flags_dist["SYN"] += 1
                                if 'A' in flags: flags_dist["ACK"] += 1
                                if 'F' in flags: flags_dist["FIN"] += 1
                                if 'R' in flags: flags_dist["RST"] += 1
                        
                        bytes_count = sum(len(p) for p in packets)
                        
                        network_evidence = {
                            "packet_count": len(packets),
                            "flow_byte_count": bytes_count,
                            "unique_src_ips": len(src_ips),
                            "unique_dst_ips": len(dst_ips),
                            "active_dst_ports": len(dst_ports),
                            "tcp_flags": flags_dist,
                            "capture_duration_sec": 5,
                            "window_start": start_time
                        }
                        
                        ws_msg = {
                            "type": "live_prediction",
                            "timestamp": time.time(),
                            "window_index": int(start_time),
                            "future_risk": result.current_risk,
                            "stage": result.predicted_stage,
                            "temporal_context": 10,
                            "forecast_horizon": 3,
                            "top_features": result.top_features,
                            "temporal_importance": result.temporal_importance,
                            "network_evidence": network_evidence,
                            "predicted_states": result.predicted_states,
                            "risk_forecast": result.risk_forecast
                        }
                        self.broadcast_sync(ws_msg)
                    else:
                        self.status = "ERROR"
                        self.error_message = "Inference engine not loaded"
                        self.broadcast_sync({"type": "error", "message": self.error_message})
                except Exception as e:
                    self.status = "ERROR"
                    self.error_message = f"Inference error: {str(e)}"
                    self.broadcast_sync({"type": "error", "message": self.error_message})
                    
        except Exception as e:
            self.status = "ERROR"
            self.error_message = f"Capture error: {str(e)}"
            self.broadcast_sync({"type": "error", "message": self.error_message})
        finally:
            if self.status != "ERROR":
                self.status = "STOPPED"

    def _extract_features(self, packets, start_time: float) -> Dict[str, float]:
        state = {}
        
        tcp_packets = 0
        udp_packets = 0
        icmp_packets = 0
        syn_count = 0
        ack_count = 0
        fin_count = 0
        rst_count = 0
        psh_count = 0
        urg_count = 0
        
        ttls = []
        tcp_windows = []
        payloads = []
        
        dst_ports = set()
        src_ports = set()
        
        for p in packets:
            if scapy.IP in p:
                ttls.append(p[scapy.IP].ttl)
            elif scapy.IPv6 in p:
                ttls.append(p[scapy.IPv6].hlim)
                
            if scapy.TCP in p:
                tcp_packets += 1
                tcp_windows.append(p[scapy.TCP].window)
                dst_ports.add(p[scapy.TCP].dport)
                src_ports.add(p[scapy.TCP].sport)
                
                flags = p[scapy.TCP].flags
                if 'S' in flags: syn_count += 1
                if 'A' in flags: ack_count += 1
                if 'F' in flags: fin_count += 1
                if 'R' in flags: rst_count += 1
                if 'P' in flags: psh_count += 1
                if 'U' in flags: urg_count += 1
                
                payload = len(p[scapy.TCP].payload)
                payloads.append(payload)
                
            elif scapy.UDP in p:
                udp_packets += 1
                dst_ports.add(p[scapy.UDP].dport)
                src_ports.add(p[scapy.UDP].sport)
                payload = len(p[scapy.UDP].payload)
                payloads.append(payload)
                
            elif scapy.ICMP in p:
                icmp_packets += 1
                
        packet_count = len(packets)
        
        state["packet_count"] = float(packet_count)
        state["tcp_packet_count"] = float(tcp_packets)
        state["udp_packet_count"] = float(udp_packets)
        state["icmp_packet_count"] = float(icmp_packets)
        
        state["syn_count"] = float(syn_count)
        state["ack_count"] = float(ack_count)
        state["fin_count"] = float(fin_count)
        state["rst_count"] = float(rst_count)
        state["psh_count"] = float(psh_count)
        state["urg_count"] = float(urg_count)
        
        if tcp_packets > 0:
            state["syn_ratio"] = syn_count / tcp_packets
            state["ack_ratio"] = ack_count / tcp_packets
            state["fin_ratio"] = fin_count / tcp_packets
            state["rst_ratio"] = rst_count / tcp_packets
            state["psh_ratio"] = psh_count / tcp_packets
            state["urg_ratio"] = urg_count / tcp_packets
            
            state["tcp_window_mean"] = float(np.mean(tcp_windows)) if tcp_windows else 0.0
            state["tcp_window_min"] = float(np.min(tcp_windows)) if tcp_windows else 0.0
            state["tcp_window_max"] = float(np.max(tcp_windows)) if tcp_windows else 0.0
            
        if ttls:
            state["ttl_mean"] = float(np.mean(ttls))
            state["ttl_min"] = float(np.min(ttls))
            state["ttl_max"] = float(np.max(ttls))
            
        if payloads:
            state["payload_mean"] = float(np.mean(payloads))
            state["payload_min"] = float(np.min(payloads))
            state["payload_max"] = float(np.max(payloads))
            
        state["unique_destination_ports"] = float(len(dst_ports))
        state["unique_source_ports"] = float(len(src_ports))
        state["port_scan_rate"] = len(dst_ports) / 5.0
        
        # All other unspecified features will default to 0.0 when mapped
        return state

live_capture_service = LiveCaptureService()
