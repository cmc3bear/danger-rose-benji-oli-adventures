#!/usr/bin/env python3
"""
Religious Compliance Tracker

Tracks specific compliance with ClaudeEthos edicts and measures
effectiveness compared to pre-religious baseline.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class ComplianceTracker:
    """Tracks religious compliance metrics over time"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.db_path = self.project_path / "religious_assessment" / "compliance.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize compliance tracking database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT,
                edict_type TEXT,
                compliance_score REAL,
                evidence TEXT,
                timestamp DATETIME,
                authenticity_score REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS effectiveness_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                pre_religious_value REAL,
                post_religious_value REAL,
                improvement_percentage REAL,
                measurement_date DATETIME
            )
        """)
        
        conn.commit()
        conn.close()
    
    def track_compliance_event(self, agent_id: str, edict_type: str, 
                             compliance_score: float, evidence: Dict[str, Any],
                             authenticity_score: float = 1.0):
        """Track a compliance event"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO compliance_events 
            (agent_id, edict_type, compliance_score, evidence, timestamp, authenticity_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            agent_id, 
            edict_type, 
            compliance_score, 
            json.dumps(evidence),
            datetime.now(),
            authenticity_score
        ))
        
        conn.commit()
        conn.close()
    
    def get_compliance_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate compliance report for specified period"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        # Overall compliance by edict
        cursor.execute("""
            SELECT edict_type, AVG(compliance_score), AVG(authenticity_score), COUNT(*)
            FROM compliance_events 
            WHERE timestamp > ?
            GROUP BY edict_type
        """, (since_date,))
        
        edict_compliance = {}
        for row in cursor.fetchall():
            edict_compliance[row[0]] = {
                "avg_compliance": row[1],
                "avg_authenticity": row[2],
                "event_count": row[3]
            }
        
        # Agent performance
        cursor.execute("""
            SELECT agent_id, AVG(compliance_score), AVG(authenticity_score), COUNT(*)
            FROM compliance_events 
            WHERE timestamp > ?
            GROUP BY agent_id
        """, (since_date,))
        
        agent_performance = {}
        for row in cursor.fetchall():
            agent_performance[row[0]] = {
                "avg_compliance": row[1],
                "avg_authenticity": row[2],
                "event_count": row[3]
            }
        
        conn.close()
        
        return {
            "period_days": days,
            "edict_compliance": edict_compliance,
            "agent_performance": agent_performance,
            "generated_at": datetime.now().isoformat()
        }
    
    def track_effectiveness_metric(self, metric_name: str, 
                                 pre_religious_value: float,
                                 post_religious_value: float):
        """Track effectiveness improvement metric"""
        
        improvement = ((post_religious_value - pre_religious_value) / pre_religious_value) * 100 if pre_religious_value != 0 else 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO effectiveness_metrics 
            (metric_name, pre_religious_value, post_religious_value, improvement_percentage, measurement_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            metric_name,
            pre_religious_value,
            post_religious_value,
            improvement,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def get_effectiveness_report(self) -> Dict[str, Any]:
        """Get effectiveness improvement report"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT metric_name, 
                   AVG(pre_religious_value), 
                   AVG(post_religious_value), 
                   AVG(improvement_percentage),
                   COUNT(*)
            FROM effectiveness_metrics
            GROUP BY metric_name
        """)
        
        effectiveness_data = {}
        for row in cursor.fetchall():
            effectiveness_data[row[0]] = {
                "avg_pre_religious": row[1],
                "avg_post_religious": row[2],
                "avg_improvement_pct": row[3],
                "measurement_count": row[4]
            }
        
        conn.close()
        
        return {
            "effectiveness_metrics": effectiveness_data,
            "generated_at": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Demo usage
    tracker = ComplianceTracker(".")
    
    # Example tracking events
    tracker.track_compliance_event("test_agent", "evidence", 0.85, {"test": "evidence"}, 0.9)
    tracker.track_effectiveness_metric("code_quality", 3.2, 4.1)  # 28% improvement
    
    print("Compliance Report:", json.dumps(tracker.get_compliance_report(), indent=2))
    print("Effectiveness Report:", json.dumps(tracker.get_effectiveness_report(), indent=2))
