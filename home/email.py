from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

class EmailSender:

    @staticmethod
    def send(to_list, from_email, template_path, subject=None, content=None, image_path=None):

        def render_mail(template_path=None, content=None):
            if content is None:
                content = {}
            
            content.update({'image_path': image_path})
            print(content)
            template = render_to_string(template_path, content)
            return template

        html_template = render_mail(template_path=template_path, content=content)
        
        mail = EmailMultiAlternatives(subject, html_template, from_email, to_list)

        mail.content_subtype = 'html'
        mail.mixed_subtype = 'related'
        mail.attach_alternative(html_template, "text/html")
        img_path = str(settings.STATIC_ROOT) + f'\\img\\{image_path}'

        if image_path:
            with open(img_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', f'<{image_path}>')
                img.add_header('Content-Disposition', 'inline', filename=image_path)
            mail.attach(img)

        return mail.send(False)