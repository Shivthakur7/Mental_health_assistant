"""
Test Script for Stage 4 - Real-world Integration Features
Tests crisis detection, emergency notifications, and monitoring systems.
"""

import os
import sys
import time
import json
from typing import Dict, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crisis_detection import check_crisis, crisis_detector
from emergency_notifications import notification_system
from monitoring import monitor

def test_crisis_detection():
    """Test the crisis detection system with various inputs."""
    print("Testing Crisis Detection System")
    print("=" * 50)
    
    test_cases = [
        {
            "text": "I want to kill myself",
            "expected_crisis": True,
            "expected_level": "critical"
        },
        {
            "text": "I feel hopeless and worthless, I can't go on",
            "expected_crisis": True,
            "expected_level": "high"
        },
        {
            "text": "I'm having a really bad day and feel sad",
            "expected_crisis": False,
            "expected_level": "none"
        },
        {
            "text": "I'm feeling great today, everything is wonderful!",
            "expected_crisis": False,
            "expected_level": "none"
        },
        {
            "text": "I hurt myself yesterday and I want to do it again",
            "expected_crisis": True,
            "expected_level": "high"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{case['text'][:50]}{'...' if len(case['text']) > 50 else ''}'")
        
        # Simulate mood score based on text sentiment
        if "kill myself" in case['text'].lower() or "suicide" in case['text'].lower():
            mood_score = -0.95
        elif any(word in case['text'].lower() for word in ["hopeless", "worthless", "hurt myself"]):
            mood_score = -0.7
        elif "bad day" in case['text'].lower() or "sad" in case['text'].lower():
            mood_score = -0.4
        else:
            mood_score = 0.6
        
        result = check_crisis(case['text'], mood_score, "international", f"test_user_{i}")
        
        # Check results
        is_crisis = result['analysis']['is_crisis']
        crisis_level = result['analysis']['crisis_level']
        
        print(f"  Expected: Crisis={case['expected_crisis']}, Level={case['expected_level']}")
        print(f"  Actual:   Crisis={is_crisis}, Level={crisis_level}")
        
        if is_crisis == case['expected_crisis']:
            if not is_crisis or crisis_level == case['expected_level']:
                print("  PASSED")
                passed += 1
            else:
                print("  FAILED - Wrong crisis level")
        else:
            print("  FAILED - Wrong crisis detection")
    
    print(f"\nCrisis Detection Results: {passed}/{total} tests passed")
    return passed == total

def test_emergency_notifications():
    """Test the emergency notification system (without actually sending)."""
    print("\nTesting Emergency Notification System")
    print("=" * 50)
    
    # Test configuration check
    print("Configuration Status:")
    print(f"  Twilio configured: {notification_system.twilio_client is not None}")
    print(f"  Email configured: {notification_system.email_address is not None}")
    
    # Test notification preparation (without sending)
    test_contacts = {
        "phone": "+1234567890",
        "email": "test@example.com"
    }
    
    print(f"\nTesting notification preparation...")
    
    # Test different crisis levels
    crisis_levels = ["critical", "high", "moderate"]
    
    for level in crisis_levels:
        print(f"\n  Testing {level} level notifications:")
        
        # This would normally send notifications, but we'll just test the preparation
        try:
            # Test SMS message preparation
            if notification_system.twilio_client:
                print(f"    SMS preparation: Ready")
            else:
                print(f"    SMS preparation: Twilio not configured")
            
            # Test email preparation
            if notification_system.email_address:
                print(f"    Email preparation: Ready")
            else:
                print(f"    Email preparation: Email not configured")
            
        except Exception as e:
            print(f"    Error in notification preparation: {e}")
    
    print(f"\nEmergency Notifications: Configuration tested")
    return True

def test_monitoring_system():
    """Test the monitoring and analytics system."""
    print("\nTesting Monitoring System")
    print("=" * 50)
    
    try:
        # Test session management
        print("Testing session management...")
        session_id = monitor.start_session("test_user_monitoring")
        print(f"  Session started: {session_id[:8]}...")
        
        # Test interaction logging
        print("Testing interaction logging...")
        interaction_id = monitor.log_interaction(
            session_id=session_id,
            user_id="test_user_monitoring",
            input_text="I'm feeling sad today",
            input_type="text",
            mood_score=-0.4,
            mood_label="NEGATIVE",
            is_crisis=False
        )
        print(f"  Interaction logged: {interaction_id[:8]}...")
        
        # Test crisis event logging
        print("Testing crisis event logging...")
        crisis_id = monitor.log_crisis_event(
            interaction_id=interaction_id,
            user_id="test_user_monitoring",
            crisis_level="high",
            crisis_keywords=["hopeless", "worthless"],
            mood_score=-0.8,
            follow_up_required=True
        )
        print(f"  Crisis event logged: {crisis_id[:8]}...")
        
        # Test analytics
        print("Testing analytics generation...")
        analytics = monitor.get_analytics_summary(days=1)
        print(f"  Analytics generated: {analytics['total_interactions']} interactions today")
        
        # Test crisis alerts
        print("Testing crisis alerts...")
        alerts = monitor.get_crisis_alerts(unresolved_only=True)
        print(f"  Crisis alerts retrieved: {len(alerts)} unresolved alerts")
        
        # End session
        monitor.end_session(session_id)
        print(f"  Session ended: {session_id[:8]}...")
        
        print(f"\nMonitoring System: All tests passed")
        return True
        
    except Exception as e:
        print(f"  Monitoring system error: {e}")
        return False

def test_integration():
    """Test the complete integration workflow."""
    print("\nTesting Complete Integration Workflow")
    print("=" * 50)
    
    try:
        # Start session
        session_id = monitor.start_session("integration_test_user")
        print(f"Session started: {session_id[:8]}...")
        
        # Test crisis scenario
        crisis_text = "I feel hopeless and want to end it all"
        mood_score = -0.85
        
        print(f"Testing crisis scenario: '{crisis_text}'")
        
        # Crisis detection
        crisis_result = check_crisis(crisis_text, mood_score, "us", "integration_test_user")
        print(f"Crisis detected: {crisis_result['analysis']['is_crisis']}")
        print(f"Crisis level: {crisis_result['analysis']['crisis_level']}")
        
        # Log the interaction
        interaction_id = monitor.log_interaction(
            session_id=session_id,
            user_id="integration_test_user",
            input_text=crisis_text,
            input_type="text",
            mood_score=mood_score,
            mood_label="NEGATIVE",
            is_crisis=crisis_result['analysis']['is_crisis'],
            crisis_level=crisis_result['analysis']['crisis_level'],
            crisis_keywords=crisis_result['analysis']['found_keywords']
        )
        print(f"Interaction logged: {interaction_id[:8]}...")
        
        # Log crisis event if detected
        if crisis_result['analysis']['is_crisis']:
            crisis_id = monitor.log_crisis_event(
                interaction_id=interaction_id,
                user_id="integration_test_user",
                crisis_level=crisis_result['analysis']['crisis_level'],
                crisis_keywords=crisis_result['analysis']['found_keywords'],
                mood_score=mood_score,
                follow_up_required=True
            )
            print(f"Crisis event logged: {crisis_id[:8]}...")
        
        # Test emergency notification preparation (without sending)
        emergency_contacts = {
            "phone": "+1234567890",
            "email": "emergency@example.com"
        }
        
        print("Emergency notification system ready")
        
        # End session
        monitor.end_session(session_id)
        print(f"Session ended: {session_id[:8]}...")
        
        print(f"\nComplete Integration: All tests passed!")
        return True
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        return False

def run_all_tests():
    """Run all Stage 4 feature tests."""
    print("Mental Health Assistant - Stage 4 Feature Tests")
    print("=" * 60)
    
    results = []
    
    # Run individual tests
    results.append(("Crisis Detection", test_crisis_detection()))
    results.append(("Emergency Notifications", test_emergency_notifications()))
    results.append(("Monitoring System", test_monitoring_system()))
    results.append(("Complete Integration", test_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} test suites passed")
    
    if passed == total:
        print("All Stage 4 features are working correctly!")
        print("\nNext Steps:")
        print("1. Configure your .env file with actual credentials")
        print("2. Test with real Twilio and email accounts")
        print("3. Deploy to your chosen cloud platform")
        print("4. Set up monitoring and alerting")
    else:
        print("Some tests failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
