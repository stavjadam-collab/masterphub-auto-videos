# VAB promo: copy for 6 languages, male/female TTS, timing json for Remotion
import asyncio, json, os, subprocess, edge_tts
P = os.path.dirname(os.path.abspath(__file__)) + '/proj'
VO = {
 'he': ('he-IL-AvriNeural', 'he-IL-HilaNeural'),
 'en': ('en-US-AndrewNeural', 'en-US-AvaNeural'),
 'es': ('es-MX-JorgeNeural', 'es-MX-DaliaNeural'),
 'fr': ('fr-FR-HenriNeural', 'fr-FR-DeniseNeural'),
 'pt': ('pt-BR-AntonioNeural', 'pt-BR-FranciscaNeural'),
 'ar': ('ar-SA-HamedNeural', 'ar-SA-ZariyahNeural'),
}
# each scene: (voice M/F, headline with *accent*, spoken line, optional caption override)
C = {
'he': dict(scenes=[
 ('M', 'יש מוצר. *אין סרטון?*', 'יש לכם מוצר טוב, ואין לכם סרטון שמוכר אותו?'),
 ('F', 'מדביקים *קישור* למוצר', 'מדביקים קישור לעמוד המוצר, ובוחרים מטרה, אורך ופלטפורמה.'),
 ('M', 'רק טענות *שנבדקו*', 'הכלי בודק מה באמת כתוב בעמוד. בלי ביקורות מומצאות, ובלי מספרים מהאוויר.'),
 ('F', '3 *כיוונים*, בוחרים אחד', 'מקבלים שלושה כיוונים לפרסומת, ובוחרים אחד.'),
 ('M', 'תסריט *מתוזמן*', 'ואז חבילת הפקה: תסריט מתוזמן, שורה אחרי שורה.'),
 ('F', 'פרומפט *לכל שוט*', 'לכל שוט יש פרומפט מוכן לכלי וידאו. מעתיקים, מדביקים, ויוצא שוט.'),
 ('M', 'קריינות, כתוביות *ומודעה*', 'וגם קריינות, כתוביות וטקסט למודעה. הכל אפשר לערוך.'),
], cta=[('F', 'שני קרדיטים לפרסומת. נרשמים בחינם, ומקבלים עשרה קרדיטים.'), ('M', 'בונה סרטוני הפרסומת, במאסטרפאב.', 'בונה סרטוני הפרסומת, ב־Masterphub')],
 ui=dict(cta='נרשמים *בחינם*', credits='קרדיטים במתנה', cost='פרסומת אחת: 2 קרדיטים', name='בונה סרטוני פרסומת ב־AI')),
'en': dict(scenes=[
 ('M', 'Great product. *No video?*', 'Got a good product, but no video that sells it?'),
 ('F', 'Paste a *link*', 'Paste the product page link, then pick your goal, length and platform.'),
 ('M', 'Only *checked* claims', 'It checks what the page really says. No fake reviews. No made up numbers.'),
 ('F', '3 *concepts*, pick one', 'You get three ad concepts. Pick one.'),
 ('M', 'A *timed* script', 'Then the production package: a timed script, line by line.'),
 ('F', 'A *prompt* for every shot', 'Every shot comes with a ready video prompt. Copy, paste, render.'),
 ('M', 'Voiceover, captions, *ad copy*', 'Plus voiceover, captions and ad copy. Everything is editable.'),
], cta=[('F', 'Two credits per ad. Sign up free and get ten credits.'), ('M', 'The AI Video Ad Builder, on Masterphub.')],
 ui=dict(cta='Sign up *free*', credits='free credits', cost='One ad costs 2 credits', name='AI Video Ad Builder')),
'es': dict(scenes=[
 ('M', 'Buen producto. *¿Sin video?*', '¿Tienes un buen producto, pero ningún video que lo venda?'),
 ('F', 'Pega un *enlace*', 'Pega el enlace de la página del producto y elige objetivo, duración y plataforma.'),
 ('M', 'Solo datos *verificados*', 'Revisa lo que la página dice de verdad. Sin reseñas falsas. Sin números inventados.'),
 ('F', '3 *conceptos*, eliges uno', 'Recibes tres conceptos de anuncio. Eliges uno.'),
 ('M', 'Un guion *con tiempos*', 'Luego, el paquete de producción: un guion con tiempos, línea por línea.'),
 ('F', 'Un *prompt* por toma', 'Cada toma trae un prompt de video listo. Copias, pegas y generas.'),
 ('M', 'Locución, subtítulos y *texto*', 'Y además locución, subtítulos y texto del anuncio. Todo se puede editar.'),
], cta=[('F', 'Dos créditos por anuncio. Regístrate gratis y recibe diez créditos.'), ('M', 'AI Video Ad Builder, en Masterphub.')],
 ui=dict(cta='Regístrate *gratis*', credits='créditos de regalo', cost='Un anuncio cuesta 2 créditos', name='AI Video Ad Builder')),
'fr': dict(scenes=[
 ('M', 'Bon produit. *Pas de vidéo ?*', 'Un bon produit, mais aucune vidéo qui le vend ?'),
 ('F', 'Collez un *lien*', "Collez le lien de la page produit, puis choisissez l'objectif, la durée et la plateforme."),
 ('M', 'Que des arguments *vérifiés*', "L'outil vérifie ce que dit vraiment la page. Pas de faux avis. Pas de chiffres inventés."),
 ('F', '3 *concepts*, un choix', 'Vous recevez trois concepts. Vous en choisissez un.'),
 ('M', 'Un script *minuté*', 'Ensuite, le dossier de production : un script minuté, ligne par ligne.'),
 ('F', 'Un *prompt* par plan', "Chaque plan a son prompt vidéo prêt à l'emploi. Copier, coller, générer."),
 ('M', 'Voix off, sous-titres, *annonce*', "Et aussi la voix off, les sous-titres et le texte de l'annonce. Tout se modifie."),
], cta=[('F', 'Deux crédits par pub. Inscription gratuite, avec dix crédits offerts.'), ('M', 'AI Video Ad Builder, sur Masterphub.')],
 ui=dict(cta='Inscription *gratuite*', credits='crédits offerts', cost='Une pub coûte 2 crédits', name='AI Video Ad Builder')),
'pt': dict(scenes=[
 ('M', 'Bom produto. *Sem vídeo?*', 'Tem um bom produto, mas nenhum vídeo que venda?'),
 ('F', 'Cole um *link*', 'Cole o link da página do produto e escolha objetivo, duração e plataforma.'),
 ('M', 'Só afirmações *verificadas*', 'A ferramenta confere o que a página diz de verdade. Sem avaliações falsas. Sem números inventados.'),
 ('F', '3 *conceitos*, escolha um', 'Você recebe três conceitos de anúncio. Escolhe um.'),
 ('M', 'Roteiro *com tempos*', 'Depois, o pacote de produção: um roteiro com tempos, linha por linha.'),
 ('F', 'Um *prompt* por cena', 'Cada cena vem com um prompt de vídeo pronto. Copie, cole e gere.'),
 ('M', 'Locução, legendas e *texto*', 'E ainda locução, legendas e texto do anúncio. Tudo editável.'),
], cta=[('F', 'Dois créditos por anúncio. Cadastre-se grátis e ganhe dez créditos.'), ('M', 'AI Video Ad Builder, na Masterphub.')],
 ui=dict(cta='Cadastre-se *grátis*', credits='créditos de presente', cost='Um anúncio custa 2 créditos', name='AI Video Ad Builder')),
'ar': dict(scenes=[
 ('M', 'منتج جيد. *بلا فيديو؟*', 'لديك منتج جيد، لكن لا يوجد فيديو يبيعه؟'),
 ('F', 'الصق *رابطًا*', 'الصق رابط صفحة المنتج، ثم اختر الهدف والمدة والمنصة.'),
 ('M', 'ادعاءات *موثّقة* فقط', 'الأداة تتحقق مما تقوله الصفحة فعلًا. لا مراجعات مزيفة، ولا أرقام مختلقة.'),
 ('F', '3 *أفكار*، اختر واحدة', 'تحصل على ثلاث أفكار للإعلان، وتختار واحدة.'),
 ('M', 'سيناريو *بالتوقيت*', 'ثم حزمة الإنتاج: سيناريو بتوقيت دقيق، سطرًا بسطر.'),
 ('F', 'برومبت *لكل لقطة*', 'لكل لقطة برومبت فيديو جاهز. انسخ، والصق، وأنشئ.'),
 ('M', 'تعليق صوتي وترجمة *ونص*', 'وأيضًا تعليق صوتي، وترجمة نصية، ونص الإعلان. وكل شيء قابل للتعديل.'),
], cta=[('F', 'رصيدان لكل إعلان. سجّل مجانًا واحصل على عشرة أرصدة.'), ('M', 'منشئ إعلانات الفيديو، على ماستر هَب.', 'AI Video Ad Builder على Masterphub')],
 ui=dict(cta='سجّل *مجانًا*', credits='رصيدًا هدية', cost='الإعلان الواحد يكلف رصيدين', name='AI Video Ad Builder')),
}
FPS = 30
def dur(f):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
async def tts(text, voice, out):
    for _ in range(3):
        try:
            await edge_tts.Communicate(text, voice, rate='+4%').save(out)
            if os.path.getsize(out) > 1000: return
        except Exception as e: print('retry', e)
async def main():
    os.makedirs(P + '/public/vo', exist_ok=True)
    out = {}
    for lang, c in C.items():
        m, f = VO[lang]
        lines = [(s[0], s[2], s[3] if len(s) > 3 else s[2]) for s in c['scenes']] + [(x[0], x[1], x[2] if len(x) > 2 else x[1]) for x in c['cta']]
        items = []
        for i, (g, say, cap) in enumerate(lines):
            fn = f'vo/{lang}_{i}.mp3'
            await tts(say, m if g == 'M' else f, P + '/public/' + fn)
            items.append(dict(file=fn, frames=round(dur(P + '/public/' + fn) * FPS), cap=cap, g=g))
        out[lang] = dict(heads=[s[1] for s in c['scenes']], vo=items, ui=c['ui'])
        print(lang, [it['frames'] for it in items])
    json.dump(out, open(P + '/src/copy.json', 'w'), ensure_ascii=False, indent=1)
asyncio.run(main())
