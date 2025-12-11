"""Message management for multi-language support."""
class Message:
    def __init__(self, language=None):
        self.language = language or "Neutral"
        self.texts = {
            "language_prompt": {
                "Neutral": "Please select your preferred language / Lütfen tercih ettiğiniz dili seçin:",
                "TR": "Lütfen tercih ettiğiniz dili seçin:",
                "EN": "Please select your preferred language:",
            },
            "continue_msg": {
                "Neutral": "Continue / Devam et",
                "TR": "Devam",
                "EN": "Continue",
            },
            "survey_title": {
                "Neutral": "RedFlag - Toxic Guy Detector / Toksik Sevgili Dedektörü",
                "TR": "RedFlag - Toksik Sevgili Dedektörü",
                "EN": "RedFlag - Toxic Guy Detector",
            },
            "welcome_message": {
                "TR": "Merhaba :blue[**{name}**]! :sunglasses:",
                "EN": "Hello :blue[**{name}**]! :sunglasses:",
            },
            "welcome_description": {
                "TR": "Burada seni görmek çok güzel. Bu anket, erkek arkadaşının ne kadar :red[toksik] olduğunu görmene yardımcı olmak için tasarlandı :bomb:",
                "EN": "It is so nice to see you here. This survey is designed to help you to see how :red[toxic] your boyfriend is :bomb:",
            },
            "welcome_instruction": {
                "TR": "Lütfen tüm soruları cevapla, böylece tüm kızlardan elde edilen sonuçları analiz edebilir ve toksik erkekleri daha iyi tespit edebiliriz.",
                "EN": "Please answer all the questions so that we can analyze the results obtained from all girls and use them to better point the toxic guys.",
            },
            "goodbye_message": {
                "TR": "Anketi tamamladığın ve geri bildirim verdiğin için teşekkürler **{name}**! :confetti_ball:",
                "EN": "Thank you for completing the survey and providing feedback **{name}**! :confetti_ball:",
            },
            "survey_complete_msg": {
                "TR": "Bitir",
                "EN": "Finish",
            },
            "filter_fail_msg": {
                "TR": "**{bf_name}**, ne yazık ki {filter_violations} tane filtrede sınıfta kaldı. Bu senin için ciddi bir uyarı anlamına gelmeli! :boom:",
                "EN": "Unfortunately **{bf_name}** failed {filter_violations} filters. This should be a critical warning for you! :boom:",
            },
            "filter_pass_msg": {
                "TR": "Güzel.. **{bf_name}** tüm filtrelerden geçti :) :blossom:",
                "EN": "Nice. **{bf_name}** satisfies all the filters :) :blossom:",
            },
            "red_flag_fail_msg": {
                "TR": "**{bf_name}** toksiklik seviyesi biraz fazla yüksek. :skull:",
                "EN": "**{bf_name}** seems to have a high level of toxicity. :skull:",
            },
            "red_flag_pass_msg": {
                "TR": "**{bf_name}** toksiklik seviyesi diğer erkeklere göre daha düşük. Aferin ona! :herb:",
                "EN": "**{bf_name}** is less toxic than many others. Good for him! :herb:",
            },
            "name_input": {"TR": "İsim", "EN": "Name"},
            "email_input": {"TR": "Eposta", "EN": "Email"},
            "bf_name_input": {"TR": "Erkek Arkadaşının İsmi", "EN": "Boyfriend's Name"},
            "filter_header": {"TR": "Filtre Sorular", "EN": "Filter Questions"},
            "redflag_header": {"TR": "Redflag Soruları", "EN": "Redflag Questions"},
            "applicability_check": {
                "TR": "Bu soru sizin için geçerli mi?",
                "EN": "Is this question applicable to you?",
            },
            "not_applicable_msg": {"TR": "Geçerli Değil", "EN": "Not Applicable"},
            "select_score_msg": {
                "TR": "Lütfen 0-10 arasında değerlendirin:",
                "EN": "Please select a score (0-10):",
            },
            "select_option_msg": {"TR": "Lütfen seçin:", "EN": "Please select:"},
            "boolean_answer": {"TR": ["Evet", "Hayır"], "EN": ["Yes", "No"]},
            "limited_opt_answer": {
                "TR": ["hiç", "1", "2", "3", "4", "5+"],
                "EN": ["never", "1", "2", "3", "4", "5+"],
            },
            "select_toxicity_msg": {
                "TR": "Peki, sence erkek arkadaşın ne kadar toksik?:",
                "EN": "So, how toxic is your boyfriend?",
            },
            "toxicity_answer": {
                "TR": [
                    "hiç değil",
                    "eh, birazcık",
                    "toksik ama herkes kadar",
                    "evet, biraz fazla toksik",
                    "gerçekten de toksik birisi",
                ],
                "EN": [
                    "not at all",
                    "a little bit",
                    "toxic but not more than others",
                    "yeah, a little more",
                    "he is literally a toxic guy",
                ],
            },
            "toxicity_result_msg": {
                "TR": "Bu, **{toxicity_rating}** toksisite derecesine karşılık geliyor.",
                "EN": "This corresponds to a toxicity rating of **{toxicity_rating}**.",
            },
            "toxic_graph_guy_cnt": {
                "TR": "Veritabanındaki erkeklerin sayısı: {guy_cnt}",
                "EN": "Number of guys in database: {guy_cnt}",
            },
            "toxic_graph_msg": {
                "TR": "Mavi nokta seninki! :large_blue_circle:",
                "EN": "blue dot is your guy! :large_blue_circle:",
            },
            "toxic_graph_x": {"TR": "indeks (skora göre sıralı)", "EN": "Index (Sorted by Score)"},
            "toxic_graph_y": {"TR": "Toksiklik", "EN": "Toxicity"},
            "category_toxicity_header": {
                "TR": "Kategori Bazında Toksisite Analizi",
                "EN": "Category-Based Toxicity Analysis",
            },
            "category_toxicity_description": {
                "TR": "Aşağıdaki grafik, {bf_name}'in hangi kategorilerde en toksik olduğunu gösterir. Skorlar 0-10 arasındadır (10 = en toksik).",
                "EN": "The chart below shows in which categories {bf_name} is most toxic. Scores range from 0-10 (10 = most toxic).",
            },
            "no_category_data_msg": {
                "TR": "Kategori verisi mevcut değil.",
                "EN": "Category data is not available.",
            },
            "feedback_msg": {"TR": "Testi ne kadar beğendin:", "EN": "How did you like the test:"},
            "please_rate_msg": {"TR": "Lütfen bir değerlendirme yapın.", "EN": "Please provide a rating."},
            "sentiment_mapping": {"TR": ["Bir", "İki", "Üç", "Dört", "Beş"], "EN": ["One", "Two", "Three", "Four", "Five"]},
            "feedback_result_msg": {"TR": "{star} :star: seçtin.", "EN": "You selected {star} :star:."},
            "rating_result_msg": {"TR": "**{selected}** seçtin", "EN": "You selected **{selected}**"},
            "toxic_saved_msg": {"TR": "Toksik değerlendirmen kaydedildi.", "EN": "Toxicity rating saved successfully!"},
            "toxic_error_msg": {
                "TR": "Toksik değerlendirme kaydedilirken hata oluştu: {e}",
                "EN": "Error saving toxicity rating: {e}",
            },
            "response_saved_msg": {"TR": "Yanıtlarınız başarıyla kaydedildi.", "EN": "Responses saved successfully!"},
            "response_error_msg": {"TR": "Yanıtlarınız kaydedilirken hata oluştu: {e}", "EN": "Error saving responses: {e}"},
            "enter_details_msg": {"TR": "Lütfen bilgilerinizi girin:", "EN": "Please enter your details:"},
            "want_email_results_msg": {
                "TR": "Sonuçları e-posta ile almak ister misiniz?",
                "EN": "Would you like to receive the results via email?",
            },
            "enter_email_if_yes_msg": {
                "TR": "Lütfen e-posta adresinizi girin:",
                "EN": "Please enter your email address:",
            },
            "enter_valid_email_msg": {
                "TR": "Lütfen geçerli bir e-posta adresi girin (örneğin, ornek@alanadi.com).",
                "EN": "Please enter a valid email address (e.g., example@domain.com).",
            },
            "email_report_info_msg": {
                "TR": "💡 E-posta adresinizi girerseniz, anket sonunda detaylı raporunuz bu adrese gönderilecektir.",
                "EN": "💡 If you provide your email address, a detailed report will be sent to this address at the end of the survey.",
            },
            "enter_name_msg": {"TR": "Lütfen adınızı girin.", "EN": "Please enter your name."},
            "report_sent_msg": {
                "TR": "Raporunuz e-posta ile gönderildi!",
                "EN": "Your report has been sent via email!",
            },
            "report_sent_to_msg": {
                "TR": "Raporunuz {email} adresine e-posta ile gönderildi!",
                "EN": "Your report has been sent via email to {email}!",
            },
            "report_skipped_msg": {
                "TR": "E-posta gönderimi atlandı.",
                "EN": "Email sending skipped.",
            },
            "contact_email_info_msg": {
                "TR": "Herhangi bir görüş veya isteğiniz için runawayguysapp@gmail.com adresine e-posta gönderebilirsiniz.",
                "EN": "For any opinions or requests, you can send an email to runawayguysapp@gmail.com.",
            },
            "enter_bf_name_msg": {"TR": "Lütfen erkek arkadaşınızın adını girin:", "EN": "Please enter your boyfriend's name:"},
            "enter_feedback_msg": {"TR": "Lütfen geri bildirim verin :gift_heart:", "EN": "Please provide feedback :gift_heart:"},
            "toxicity_header": {
                "TR": "Haydi erkek arkadaşının toksikliğini değerlendirelim :tulip:",
                "EN": "Let's evaluate your boyfriend's toxicity :tulip:",
            },
            "fill_before_submit_msg": {"TR": "Göndermeden önce lütfen soruları yanıtlayın.", "EN": "Please complete the questions before submitting."},
            "name_submit_msg": {"TR": "Göndermeden önce lütfen adınızı girin.", "EN": "Please enter your name before submitting."},
            "gtk_header": {"TR": "Seni tanıyalım :clipboard:", "EN": "Let's get to know you :clipboard:"},
            "toxicity_self_rating": {"TR": "Sence, erkek arkadaşın ne kadar toksik.. :man_dancing:", "EN": "How do you think your boyfriend is toxic.. :man_dancing:"},
            "result_header": {"TR": "Sonuç :dizzy:", "EN": "Result :dizzy:"},
            "start_new_survey": {"TR": "Yeni Anket Başlat", "EN": "Start New Survey"},
            "toxic_score_info": {"TR": "Erkek arkadaşının toksiklik skoru: %{toxic_score}", "EN": "Your boyfriend's toxicity score is: {toxic_score}%"},
            "filter_viol_info": {"TR": "Genelde {avg_filter_violations} filtreye takılıyor erkekler.", "EN": "Generally, guys fail in {avg_filter_violations} filters."},
            "see_results": {"TR": "Sonucu gör", "EN": "See the result"},
            "insights_header": {"TR": "AI İçgörüleri", "EN": "AI-Generated Insights"},
            "generating_insights_msg": {
                "TR": "Kişiselleştirilmiş içgörüler oluşturuluyor...",
                "EN": "Generating personalized insights...",
            },
            "insights_unavailable_msg": {
                "TR": "AI içgörüleri mevcut değil. LLM API yapılandırılmamış.",
                "EN": "AI insights are not available. LLM API is not configured.",
            },
            "insights_disclaimer": {
                "TR": "**Not:** Bu basit bir analizdir ve yanlış olabilir. Lütfen ciddiye almayın, sadece dikkate alın.",
                "EN": "**Note:** This is a simple analysis and may be wrong. Please do not take it seriously, just take it into account simply.",
            },
        }

    def get(self, key, **kwargs):
        """
        Get text based on current language with fallback order:
        1. Current language
        2. Neutral
        3. English
        """
        candidates = [
            self.texts.get(key, {}).get(self.language),
            self.texts.get(key, {}).get("Neutral"),
            self.texts.get(key, {}).get("EN"),
        ]
        for text in candidates:
            if text:
                if isinstance(text, str):
                    return text.format(**kwargs)
                return text
        return f"[Missing text: {key}]"

    def get_any(self, key, **kwargs):
        """
        Force return the Neutral version of a text.
        Useful before language is chosen (AskLanguage step).
        """
        text = self.texts.get(key, {}).get("Neutral")
        if text:
            if isinstance(text, str):
                return text.format(**kwargs)
            return text
        return f"[Missing neutral text: {key}]"

