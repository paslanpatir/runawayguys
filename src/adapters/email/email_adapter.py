"""Email adapter implementation using SMTP."""
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Tuple
from src.infrastructure.email_connection_manager import EmailConnectionManager
from src.ports.email_port import EmailPort


class EmailAdapter(EmailPort):
    """SMTP implementation of EmailPort."""

    def __init__(self):
        """Initialize email adapter using EmailConnectionManager."""
        self.conn_manager = EmailConnectionManager()
        self.credentials = self.conn_manager.get_credentials()
        
        self.smtp_server = self.credentials["smtp_server"]
        self.smtp_port = self.credentials["smtp_port"]
        self.sender_email = self.credentials["sender_email"]
        self.sender_password = self.credentials["sender_password"]

    def send_report(
        self,
        recipient_email: str,
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]] = None,
        language: str = "EN",
        insights: str = None,
    ) -> bool:
        """
        Send survey results report via email.
        
        Args:
            recipient_email: Email address to send to
            user_name: Name of the user
            bf_name: Boyfriend's name
            toxic_score: Toxicity score (0-1)
            avg_toxic_score: Average toxicity score from all users (0-1)
            filter_violations: Number of filter violations
            violated_filter_questions: List of violated filter questions
            language: Language code (TR or EN)
            insights: AI-generated insights (optional)
            toxic_plot_image: PNG image bytes for toxic plot (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.sender_email or not self.sender_password:
            print("[WARNING] Email credentials not configured. Set SENDER_EMAIL and SENDER_PASSWORD environment variables or configure config/email_credentials.txt")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = recipient_email
            msg["Subject"] = self._get_subject(language, bf_name)

            # Create email body
            body = self._create_email_body(
                user_name, bf_name, toxic_score, avg_toxic_score,
                filter_violations, violated_filter_questions, language, insights
            )
            msg.attach(MIMEText(body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            print(f"[OK] Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            print(f"[ERROR] Error sending email: {e}")
            return False

    def close(self) -> None:
        """Close the connection manager."""
        self.conn_manager.close()

    def _get_subject(self, language: str, bf_name: str) -> str:
        """Get email subject based on language."""
        if language == "TR":
            return f"RedFlag - {bf_name} Toksiklik Raporu"
        return f"RedFlag - {bf_name} Toxicity Report"

    def _create_email_body(
        self,
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]] = None,
        language: str = "EN",
        insights: str = None,
    ) -> str:
        """Create HTML email body with survey results and insights."""
        score_percentage = round(toxic_score * 100, 1)
        avg_score_percentage = round(avg_toxic_score * 100, 1)
        
        # Format violated filter questions
        violated_filters_html = ""
        if violated_filter_questions:
            if language == "TR":
                violated_filters_html = "<h4 style='margin-top: 10px;'>İhlal Edilen Filtreler:</h4><ul style='margin-top: 5px;'>"
                for question_text, answer, f_id in violated_filter_questions:
                    violated_filters_html += f"<li>{question_text}</li>"
                violated_filters_html += "</ul>"
            else:
                violated_filters_html = "<h4 style='margin-top: 10px;'>Violated Filters:</h4><ul style='margin-top: 5px;'>"
                for question_text, answer, f_id in violated_filter_questions:
                    violated_filters_html += f"<li>{question_text}</li>"
                violated_filters_html += "</ul>"
        
        # Format insights for HTML
        insights_html = ""
        if insights:
            if language == "TR":
                insights_html = f"""
                        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #2196f3;">
                            <h3 style="margin-top: 0; color: #1976d2;">🤖 AI İçgörüleri</h3>
                            <p style="white-space: pre-wrap;">{insights}</p>
                        </div>
                """
            else:
                insights_html = f"""
                        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #2196f3;">
                            <h3 style="margin-top: 0; color: #1976d2;">🤖 AI Insights</h3>
                            <p style="white-space: pre-wrap;">{insights}</p>
                        </div>
                """

        if language == "TR":
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #d32f2f;">🚩 RedFlag - Toksiklik Raporu</h2>
                        <p>Merhaba <strong>{user_name}</strong>,</p>
                        <p>Anket sonuçlarınız hazır! İşte <strong>{bf_name}</strong> için toksiklik analizi:</p>
                        
                        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="margin-top: 0;">📊 Sonuçlar</h3>
                            <p><strong>Toksiklik Skoru:</strong> {score_percentage}%</p>
                            <p><strong>Ortalama Toksisite Skoru:</strong> {avg_score_percentage}%</p>
                            <p><strong>Filtre İhlalleri:</strong> {filter_violations}</p>
                            {violated_filters_html}
                        </div>
                        {insights_html}
                        <p>Detaylı rapor ve grafikler için web sitesini ziyaret edebilirsiniz.</p>
                        
                        <p style="margin-top: 30px; color: #666; font-size: 12px;">
                            Bu e-posta otomatik olarak gönderilmiştir. Lütfen yanıtlamayın.
                        </p>
                    </div>
                </body>
            </html>
            """
        else:
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #d32f2f;">🚩 RedFlag - Toxicity Report</h2>
                        <p>Hello <strong>{user_name}</strong>,</p>
                        <p>Your survey results are ready! Here's the toxicity analysis for <strong>{bf_name}</strong>:</p>
                        
                        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="margin-top: 0;">📊 Results</h3>
                            <p><strong>Toxicity Score:</strong> {score_percentage}%</p>
                            <p><strong>Average Toxicity Score:</strong> {avg_score_percentage}%</p>
                            <p><strong>Filter Violations:</strong> {filter_violations}</p>
                            {violated_filters_html}
                        </div>
                        {insights_html}
                        <p>Visit our website for detailed reports and graphs.</p>
                        
                        <p style="margin-top: 30px; color: #666; font-size: 12px;">
                            This email was sent automatically. Please do not reply.
                        </p>
                    </div>
                </body>
            </html>
            """
        return html


def send_survey_report(
    recipient_email: str,
    session_data: dict,
    language: str = "EN",
) -> bool:
    """
    Convenience function to send survey report.
    
    Args:
        recipient_email: Email address to send to
        session_data: Dictionary containing session data with keys:
            - user_details: dict with 'name', 'bf_name'
            - toxic_score: float
            - filter_violations: int
            - ai_insights: str (optional) - AI-generated insights
        language: Language code (TR or EN)
        
    Returns:
        True if email sent successfully, False otherwise
    """
    sender = EmailAdapter()
    
    user_details = session_data.get("user_details", {})
    toxic_score = session_data.get("toxic_score", 0)
    avg_toxic_score = session_data.get("avg_toxic_score", 0.5)
    filter_violations = session_data.get("filter_violations", 0)
    violated_filter_questions = session_data.get("violated_filter_questions")
    insights = session_data.get("ai_insights")
    
    return sender.send_report(
        recipient_email=recipient_email,
        user_name=user_details.get("name", "User"),
        bf_name=user_details.get("bf_name", "Your boyfriend"),
        toxic_score=toxic_score,
        avg_toxic_score=avg_toxic_score,
        filter_violations=filter_violations,
        violated_filter_questions=violated_filter_questions,
        language=language,
        insights=insights,
    )

