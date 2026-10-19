# HeyGen — דמות מדברת

- להשתמש ב-API ישירות, לא בעורך AI Studio. בעורך, שינויים שנשמעים נכון בתצוגה המקדימה לא תמיד נשמרים בסרטון הסופי.
- קול: "stav adam" (voice_id 818730de0c0f461dbe04f525dcb0f82d) עם ElevenLabs v3 (`eleven_v3`), עברית.
- אווטאר תמונה: talking_photo_id 5907458528f346ab90c881354db619df ("Stavv4 the podcast host"), 1080x1920.
- בלי תגיות רגש בטקסט (כמו [confidently]). הן משנות את הקול.
- טקסט בעברית עם ניקוד מלא, בכל התסריט ולא רק במילה הבעייתית.
- זרימה: POST /v2/video/generate → בדיקה כל 30 שניות ב-/v1/video_status.get?video_id=... → הורדה מ-video_url.
- את תנועת הידיים אי אפשר לשלוט בה דרך ה-API של אווטאר תמונה.
- המפתח שמור אצל סתיו (לא כאן).
- פרטים מלאים: מסמך הפרויקט claude/resharp-heygen-script.md.
