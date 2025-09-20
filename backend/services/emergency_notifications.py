"""
Emergency Notification System for Mental Health Assistant
Handles SMS and email notifications for crisis situations.
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmergencyNotificationSystem:
    def __init__(self):
        # Twilio configuration (from environment variables)
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Email configuration (from environment variables)
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        
        # Initialize Twilio client if credentials are available
        self.twilio_client = None
        self._initialize_twilio()

    def _initialize_twilio(self):
        """Initialize Twilio client if credentials are available."""
        try:
            if self.twilio_sid and self.twilio_auth_token:
                from twilio.rest import Client
                self.twilio_client = Client(self.twilio_sid, self.twilio_auth_token)
                logger.info("Twilio client initialized successfully")
            else:
                logger.warning("Twilio credentials not found. SMS notifications will be disabled.")
        except ImportError:
            logger.warning("Twilio library not installed. SMS notifications will be disabled.")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")

    def send_crisis_sms(self, contact_number: str, user_name: str = "User", crisis_level: str = "high") -> Dict:
        """
        Send crisis alert SMS to emergency contact.
        
        Args:
            contact_number: Emergency contact phone number
            user_name: Name of the user in crisis
            crisis_level: Level of crisis (critical, high, moderate)
            
        Returns:
            Dictionary with send status and details
        """
        if not self.twilio_client or not self.twilio_phone_number:
            return {
                "success": False,
                "error": "Twilio not configured",
                "message": "SMS notifications are not available"
            }
        
        try:
            # Customize message based on crisis level
            if crisis_level == "critical":
                message = f"""🚨 URGENT MENTAL HEALTH ALERT 🚨

{user_name} has indicated they may be in immediate crisis and expressed thoughts of self-harm or suicide.

This is an automated alert from their Mental Health Assistant app.

IMMEDIATE ACTION RECOMMENDED:
• Contact {user_name} immediately
• Encourage them to call emergency services (911)
• Consider calling emergency services yourself if you cannot reach them

Crisis resources:
• 988 Suicide & Crisis Lifeline: 988
• Emergency: 911
• Crisis Text Line: Text HOME to 741741

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This person trusts you. Please reach out to them now."""

            elif crisis_level == "high":
                message = f"""⚠️ MENTAL HEALTH CONCERN ALERT ⚠️

{user_name} has expressed concerning thoughts and may need support.

This is an automated alert from their Mental Health Assistant app.

RECOMMENDED ACTIONS:
• Check in with {user_name} when possible
• Offer emotional support and listen
• Encourage professional help if needed

Crisis resources if needed:
• 988 Suicide & Crisis Lifeline: 988
• Crisis Text Line: Text HOME to 741741

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Your support could make a difference."""

            else:  # moderate
                message = f"""💙 MENTAL HEALTH CHECK-IN ALERT

{user_name} may be going through a difficult time and could benefit from support.

This is an automated alert from their Mental Health Assistant app.

SUGGESTED ACTIONS:
• Reach out to {user_name} when convenient
• Offer a listening ear
• Check in on their wellbeing

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Sometimes just knowing someone cares makes all the difference."""

            # Send SMS
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=contact_number
            )
            
            logger.info(f"Crisis SMS sent successfully. SID: {message_obj.sid}")
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "to": contact_number,
                "crisis_level": crisis_level,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send crisis SMS: {e}")
            return {
                "success": False,
                "error": str(e),
                "to": contact_number,
                "crisis_level": crisis_level,
                "timestamp": datetime.now().isoformat()
            }

    def send_crisis_email(self, contact_email: str, user_name: str = "User", crisis_level: str = "high", additional_context: str = "") -> Dict:
        """
        Send crisis alert email to emergency contact.
        
        Args:
            contact_email: Emergency contact email address
            user_name: Name of the user in crisis
            crisis_level: Level of crisis (critical, high, moderate)
            additional_context: Additional context about the situation
            
        Returns:
            Dictionary with send status and details
        """
        if not self.email_address or not self.email_password:
            return {
                "success": False,
                "error": "Email not configured",
                "message": "Email notifications are not available"
            }
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = contact_email
            
            if crisis_level == "critical":
                msg['Subject'] = f"🚨 URGENT: Mental Health Crisis Alert for {user_name}"
                body = f"""
<html>
<body>
<h2 style="color: #d32f2f;">🚨 URGENT MENTAL HEALTH CRISIS ALERT 🚨</h2>

<p><strong>{user_name}</strong> has indicated they may be in immediate crisis and expressed thoughts of self-harm or suicide.</p>

<p>This is an automated alert from their Mental Health Assistant application.</p>

<div style="background-color: #ffebee; padding: 15px; border-left: 4px solid #d32f2f; margin: 20px 0;">
<h3 style="color: #d32f2f; margin-top: 0;">IMMEDIATE ACTION RECOMMENDED:</h3>
<ul>
<li><strong>Contact {user_name} immediately</strong></li>
<li>Encourage them to call emergency services (911)</li>
<li>Consider calling emergency services yourself if you cannot reach them</li>
<li>Stay with them or ensure someone trustworthy is with them</li>
</ul>
</div>

<h3>Crisis Resources:</h3>
<ul>
<li><strong>988 Suicide & Crisis Lifeline:</strong> 988 (24/7)</li>
<li><strong>Emergency Services:</strong> 911</li>
<li><strong>Crisis Text Line:</strong> Text HOME to 741741</li>
<li><strong>International:</strong> <a href="https://findahelpline.com">findahelpline.com</a></li>
</ul>

{f"<h3>Additional Context:</h3><p>{additional_context}</p>" if additional_context else ""}

<p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<p style="font-style: italic; color: #666;">This person trusts you enough to list you as their emergency contact. Please reach out to them now. Your immediate response could save a life.</p>

<hr>
<p style="font-size: 12px; color: #888;">This alert was generated automatically by the Mental Health Assistant application. If you believe this is an error, please still check on {user_name} to be safe.</p>
</body>
</html>
"""

            elif crisis_level == "high":
                msg['Subject'] = f"⚠️ Mental Health Concern Alert for {user_name}"
                body = f"""
<html>
<body>
<h2 style="color: #f57c00;">⚠️ MENTAL HEALTH CONCERN ALERT ⚠️</h2>

<p><strong>{user_name}</strong> has expressed concerning thoughts and may need support.</p>

<p>This is an automated alert from their Mental Health Assistant application.</p>

<div style="background-color: #fff3e0; padding: 15px; border-left: 4px solid #f57c00; margin: 20px 0;">
<h3 style="color: #f57c00; margin-top: 0;">RECOMMENDED ACTIONS:</h3>
<ul>
<li>Check in with {user_name} when possible</li>
<li>Offer emotional support and listen without judgment</li>
<li>Encourage professional help if the situation seems serious</li>
<li>Be patient and understanding</li>
</ul>
</div>

<h3>Crisis Resources (if needed):</h3>
<ul>
<li><strong>988 Suicide & Crisis Lifeline:</strong> 988 (24/7)</li>
<li><strong>Crisis Text Line:</strong> Text HOME to 741741</li>
<li><strong>International:</strong> <a href="https://findahelpline.com">findahelpline.com</a></li>
</ul>

{f"<h3>Additional Context:</h3><p>{additional_context}</p>" if additional_context else ""}

<p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<p style="font-style: italic; color: #666;">Your support could make a significant difference in {user_name}'s wellbeing.</p>

<hr>
<p style="font-size: 12px; color: #888;">This alert was generated automatically by the Mental Health Assistant application.</p>
</body>
</html>
"""

            else:  # moderate
                msg['Subject'] = f"💙 Mental Health Check-in for {user_name}"
                body = f"""
<html>
<body>
<h2 style="color: #1976d2;">💙 MENTAL HEALTH CHECK-IN ALERT</h2>

<p><strong>{user_name}</strong> may be going through a difficult time and could benefit from support.</p>

<p>This is an automated alert from their Mental Health Assistant application.</p>

<div style="background-color: #e3f2fd; padding: 15px; border-left: 4px solid #1976d2; margin: 20px 0;">
<h3 style="color: #1976d2; margin-top: 0;">SUGGESTED ACTIONS:</h3>
<ul>
<li>Reach out to {user_name} when convenient</li>
<li>Offer a listening ear</li>
<li>Check in on their general wellbeing</li>
<li>Suggest positive activities you could do together</li>
</ul>
</div>

{f"<h3>Context:</h3><p>{additional_context}</p>" if additional_context else ""}

<p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<p style="font-style: italic; color: #666;">Sometimes just knowing someone cares makes all the difference.</p>

<hr>
<p style="font-size: 12px; color: #888;">This alert was generated automatically by the Mental Health Assistant application.</p>
</body>
</html>
"""

            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_address, contact_email, text)
            server.quit()
            
            logger.info(f"Crisis email sent successfully to {contact_email}")
            
            return {
                "success": True,
                "to": contact_email,
                "crisis_level": crisis_level,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send crisis email: {e}")
            return {
                "success": False,
                "error": str(e),
                "to": contact_email,
                "crisis_level": crisis_level,
                "timestamp": datetime.now().isoformat()
            }

    def send_crisis_notifications(self, emergency_contacts: Dict, user_name: str = "User", crisis_level: str = "high", additional_context: str = "") -> Dict:
        """
        Send crisis notifications to all configured emergency contacts.
        
        Args:
            emergency_contacts: Dict with 'phone' and/or 'email' keys
            user_name: Name of the user in crisis
            crisis_level: Level of crisis
            additional_context: Additional context about the situation
            
        Returns:
            Dictionary with results for all notification attempts
        """
        results = {
            "notifications_sent": [],
            "notifications_failed": [],
            "total_attempted": 0,
            "total_successful": 0
        }
        
        # Send SMS notifications
        if "phone" in emergency_contacts and emergency_contacts["phone"]:
            results["total_attempted"] += 1
            sms_result = self.send_crisis_sms(
                emergency_contacts["phone"], 
                user_name, 
                crisis_level
            )
            
            if sms_result["success"]:
                results["notifications_sent"].append({
                    "type": "sms",
                    "to": emergency_contacts["phone"],
                    "result": sms_result
                })
                results["total_successful"] += 1
            else:
                results["notifications_failed"].append({
                    "type": "sms",
                    "to": emergency_contacts["phone"],
                    "error": sms_result["error"]
                })
        
        # Send email notifications
        if "email" in emergency_contacts and emergency_contacts["email"]:
            results["total_attempted"] += 1
            email_result = self.send_crisis_email(
                emergency_contacts["email"], 
                user_name, 
                crisis_level, 
                additional_context
            )
            
            if email_result["success"]:
                results["notifications_sent"].append({
                    "type": "email",
                    "to": emergency_contacts["email"],
                    "result": email_result
                })
                results["total_successful"] += 1
            else:
                results["notifications_failed"].append({
                    "type": "email",
                    "to": emergency_contacts["email"],
                    "error": email_result["error"]
                })
        
        logger.info(f"Crisis notifications: {results['total_successful']}/{results['total_attempted']} successful")
        
        return results

# Global notification system instance
notification_system = EmergencyNotificationSystem()

def send_emergency_alert(emergency_contacts: Dict, user_name: str = "User", crisis_level: str = "high", additional_context: str = "") -> Dict:
    """
    Convenience function to send emergency alerts.
    
    Args:
        emergency_contacts: Dict with contact information
        user_name: Name of the user in crisis
        crisis_level: Level of crisis
        additional_context: Additional context
        
    Returns:
        Notification results
    """
    return notification_system.send_crisis_notifications(
        emergency_contacts, 
        user_name, 
        crisis_level, 
        additional_context
    )

if __name__ == "__main__":
    # Test the notification system (with dummy data)
    print("Emergency Notification System Test")
    print("=" * 40)
    
    # Test configuration check
    print(f"Twilio configured: {notification_system.twilio_client is not None}")
    print(f"Email configured: {notification_system.email_address is not None}")
    
    # Example usage (commented out to avoid sending actual notifications)
    """
    test_contacts = {
        "phone": "+1234567890",  # Replace with actual test number
        "email": "test@example.com"  # Replace with actual test email
    }
    
    result = send_emergency_alert(
        emergency_contacts=test_contacts,
        user_name="Test User",
        crisis_level="high",
        additional_context="This is a test of the emergency notification system."
    )
    
    print(f"Notification results: {result}")
    """
