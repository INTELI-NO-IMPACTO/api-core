from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Iterable

from fastapi import HTTPException, status

from ..config import settings


class EmailNotConfiguredError(RuntimeError):
    """Raised when SMTP configuration is missing."""


class EmailService:
    """Simple SMTP email sender backed by Gmail or compatible servers."""

    def __init__(
        self,
        host: str | None,
        port: int | None,
        username: str | None,
        password: str | None,
        sender: str | None,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sender = sender

    @property
    def is_configured(self) -> bool:
        return all([self.host, self.port, self.username, self.password, self.sender])

    def _ensure_configured(self) -> None:
        if not self.is_configured:
            raise EmailNotConfiguredError("Configuração SMTP ausente. Verifique variáveis SMTP_* no .env.")

    def send_email(
        self,
        subject: str,
        recipients: str | Iterable[str],
        *,
        text_body: str | None = None,
        html_body: str | None = None,
        reply_to: str | None = None,
    ) -> None:
        self._ensure_configured()

        if isinstance(recipients, str):
            recipients_list = [recipients]
        else:
            recipients_list = list(recipients)

        if not recipients_list:
            raise ValueError("Pelo menos um destinatário é necessário.")

        if not text_body and not html_body:
            raise ValueError("É necessário fornecer texto ou HTML para o corpo do email.")

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.sender
        message["To"] = ", ".join(recipients_list)
        if reply_to:
            message["Reply-To"] = reply_to

        if text_body:
            message.set_content(text_body)
        if html_body:
            message.add_alternative(html_body, subtype="html")

        try:
            if self.port == 465:
                with smtplib.SMTP_SSL(self.host, self.port) as smtp:
                    smtp.login(self.username, self.password)
                    smtp.send_message(message)
            else:
                with smtplib.SMTP(self.host, self.port) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.login(self.username, self.password)
                    smtp.send_message(message)
        except smtplib.SMTPException as exc:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                f"Falha ao enviar email: {exc}",
            ) from exc


def get_email_service() -> EmailService:
    return EmailService(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        settings.SMTP_USER,
        settings.SMTP_PASS,
        settings.SMTP_FROM,
    )


def send_invite_email(email_service: EmailService, *, recipient: str, invite_code: str, org_name: str) -> None:
    subject = f"Convite para participar da ONG {org_name} - Instituto Impacto Social"
    text = (
        f"Olá!\n\n"
        f"Você foi convidado para fazer parte da equipe da ONG {org_name} no Instituto Impacto Social.\n\n"
        f"O Instituto Impacto Social é uma plataforma digital formada por um site e um chatbot inteligente "
        f"que facilita o acesso a serviços públicos para pessoas trans — um dos grupos que mais enfrentam "
        f"barreiras burocráticas, falta de informação e preconceito ao acessar seus direitos.\n\n"
        f"A plataforma coleta apenas as informações essenciais do usuário e utiliza IA para analisar "
        f"elegibilidade e recomendar exatamente os serviços que aquela pessoa pode acessar, como retificação "
        f"de nome e gênero no registro civil, atendimento especializado no SUS, programas de proteção social "
        f"e apoio psicossocial. Além disso, oferece tutoriais simples e acessíveis, explicando passo a passo "
        f"como solicitar os benefícios indicados.\n\n"
        f"Para aceitar o convite e criar sua conta, use o código abaixo durante o cadastro:\n\n"
        f"{invite_code}\n\n"
        f"Com este código, você terá acesso à plataforma e poderá colaborar nas atividades da {org_name}.\n\n"
        "Se você não esperava este email, pode ignorá-lo com segurança.\n"
    )
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Convite - {org_name}</title>
    </head>
    <body style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;background-color:#f4f4f7;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f7;padding:40px 20px;">
            <tr>
                <td align="center">
                    <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background-color:#ffffff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.05);overflow:hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:40px 30px;text-align:center;">
                                <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:700;letter-spacing:-0.5px;">
                                    Instituto Impacto Social
                                </h1>
                            </td>
                        </tr>

                        <!-- Content -->
                        <tr>
                            <td style="padding:40px 30px;">
                                <h2 style="margin:0 0 20px;color:#1a202c;font-size:24px;font-weight:600;">
                                    Olá!
                                </h2>
                                <p style="margin:0 0 20px;color:#4a5568;font-size:16px;line-height:1.6;">
                                    Você foi convidado para fazer parte da equipe da ONG <strong style="color:#667eea;">{org_name}</strong> no Instituto Impacto Social.
                                </p>

                                <!-- About Platform Box -->
                                <div style="background-color:#f8f9ff;border-left:4px solid #667eea;border-radius:8px;padding:20px;margin:0 0 24px;">
                                    <p style="margin:0 0 12px;color:#1a202c;font-size:15px;font-weight:600;">
                                        Sobre a plataforma:
                                    </p>
                                    <p style="margin:0;color:#4a5568;font-size:14px;line-height:1.6;">
                                        O Instituto Impacto Social é uma plataforma digital formada por um <strong>site e um chatbot inteligente</strong> que facilita o acesso a serviços públicos para <strong>pessoas trans</strong> — um dos grupos que mais enfrentam barreiras burocráticas, falta de informação e preconceito ao acessar seus direitos.
                                    </p>
                                </div>

                                <p style="margin:0 0 16px;color:#4a5568;font-size:15px;line-height:1.6;">
                                    A plataforma coleta apenas as informações essenciais e utiliza <strong>IA</strong> para analisar elegibilidade e recomendar serviços como:
                                </p>
                                <ul style="margin:0 0 24px;padding-left:20px;color:#4a5568;font-size:14px;line-height:1.8;">
                                    <li>Retificação de nome e gênero no registro civil</li>
                                    <li>Atendimento especializado no SUS</li>
                                    <li>Programas de proteção social</li>
                                    <li>Apoio psicossocial</li>
                                </ul>

                                <p style="margin:0 0 24px;color:#4a5568;font-size:15px;line-height:1.6;">
                                    Além disso, oferece <strong>tutoriais simples e acessíveis</strong>, explicando passo a passo como solicitar os benefícios indicados.
                                </p>

                                <p style="margin:0 0 16px;color:#4a5568;font-size:16px;line-height:1.6;font-weight:600;">
                                    Para aceitar o convite e criar sua conta, use o código abaixo durante o cadastro:
                                </p>

                                <!-- Invite Code Box -->
                                <div style="background-color:#f7fafc;border:2px dashed #667eea;border-radius:8px;padding:24px;text-align:center;margin:0 0 24px;">
                                    <div style="color:#667eea;font-size:32px;font-weight:700;letter-spacing:4px;font-family:monospace;">
                                        {invite_code}
                                    </div>
                                </div>

                                <p style="margin:0;color:#718096;font-size:14px;line-height:1.6;">
                                    Se você não esperava este email, pode ignorá-lo com segurança.
                                </p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background-color:#f7fafc;padding:30px;text-align:center;border-top:1px solid #e2e8f0;">
                                <p style="margin:0 0 8px;color:#718096;font-size:13px;">
                                    Instituto Impacto Social
                                </p>
                                <p style="margin:0;color:#a0aec0;font-size:12px;">
                                    Transformando vidas através da solidariedade
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    email_service.send_email(subject, recipient, text_body=text, html_body=html)


def send_org_validation_email(
    email_service: EmailService,
    *,
    recipient: str,
    org_name: str,
    approval_status: bool,
    reason: str | None = None,
) -> None:
    if approval_status:
        subject = f"ONG {org_name} aprovada - Instituto Impacto Social"
        text = (
            f"Parabéns!\n\n"
            f"Sua ONG {org_name} foi aprovada na plataforma Instituto Impacto Social!\n\n"
            f"O Instituto Impacto Social é uma plataforma digital que facilita o acesso a serviços públicos "
            f"para pessoas trans, utilizando IA para recomendar serviços como retificação de documentos, "
            f"atendimento no SUS, programas sociais e apoio psicossocial.\n\n"
            f"Agora você pode:\n"
            f"- Gerenciar beneficiários da sua ONG\n"
            f"- Acompanhar solicitações de serviços\n"
            f"- Criar e publicar artigos educativos\n"
            f"- Acessar tutoriais e recursos da plataforma\n\n"
            "Boas-vindas à rede de transformação social!\n"
        )
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ONG Aprovada - {org_name}</title>
        </head>
        <body style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;background-color:#f4f4f7;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f7;padding:40px 20px;">
                <tr>
                    <td align="center">
                        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background-color:#ffffff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.05);overflow:hidden;">
                            <!-- Header -->
                            <tr>
                                <td style="background:linear-gradient(135deg,#48bb78 0%,#38a169 100%);padding:40px 30px;text-align:center;">
                                    <div style="width:64px;height:64px;background-color:rgba(255,255,255,0.2);border-radius:50%;margin:0 auto 20px;display:flex;align-items:center;justify-content:center;">
                                        <div style="font-size:40px;">✓</div>
                                    </div>
                                    <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:700;letter-spacing:-0.5px;">
                                        Parabéns!
                                    </h1>
                                </td>
                            </tr>

                            <!-- Content -->
                            <tr>
                                <td style="padding:40px 30px;">
                                    <h2 style="margin:0 0 20px;color:#1a202c;font-size:24px;font-weight:600;text-align:center;">
                                        Sua ONG foi aprovada!
                                    </h2>
                                    <p style="margin:0 0 24px;color:#4a5568;font-size:16px;line-height:1.6;text-align:center;">
                                        A ONG <strong style="color:#38a169;">{org_name}</strong> foi aprovada com sucesso na plataforma Instituto Impacto Social.
                                    </p>

                                    <!-- About Platform Box -->
                                    <div style="background-color:#f0fdf4;border-left:4px solid #38a169;border-radius:8px;padding:20px;margin:0 0 24px;">
                                        <p style="margin:0 0 12px;color:#166534;font-size:15px;font-weight:600;">
                                            Sobre a plataforma:
                                        </p>
                                        <p style="margin:0;color:#166534;font-size:14px;line-height:1.6;">
                                            O Instituto Impacto Social é uma plataforma digital que facilita o acesso a serviços públicos para <strong>pessoas trans</strong>, utilizando IA para recomendar serviços como retificação de documentos, atendimento no SUS, programas sociais e apoio psicossocial.
                                        </p>
                                    </div>

                                    <!-- Success Box -->
                                    <div style="background-color:#f8f9ff;border-left:4px solid #667eea;border-radius:8px;padding:20px;margin:0 0 24px;">
                                        <p style="margin:0 0 12px;color:#1a202c;font-size:15px;font-weight:600;">
                                            O que você pode fazer agora:
                                        </p>
                                        <ul style="margin:0;padding-left:20px;color:#4a5568;font-size:14px;line-height:1.8;">
                                            <li>Gerenciar beneficiários da sua ONG</li>
                                            <li>Acompanhar solicitações de serviços</li>
                                            <li>Criar e publicar artigos educativos</li>
                                            <li>Acessar tutoriais e recursos da plataforma</li>
                                        </ul>
                                    </div>

                                    <p style="margin:0;color:#718096;font-size:14px;line-height:1.6;text-align:center;">
                                        Estamos felizes em tê-los conosco nessa jornada de transformação social!
                                    </p>
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="background-color:#f7fafc;padding:30px;text-align:center;border-top:1px solid #e2e8f0;">
                                    <p style="margin:0 0 8px;color:#718096;font-size:13px;">
                                        Instituto Impacto Social
                                    </p>
                                    <p style="margin:0;color:#a0aec0;font-size:12px;">
                                        Transformando vidas através da solidariedade
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
    else:
        subject = f"Análise da solicitação - ONG {org_name}"
        reason_text = f"Motivo: {reason or 'Motivo não informado'}\n"
        reason_html = f"""
                                    <div style="background-color:#fef2f2;border-left:4px solid #ef4444;border-radius:8px;padding:20px;margin:0 0 24px;">
                                        <p style="margin:0;color:#991b1b;font-size:15px;line-height:1.6;">
                                            <strong>Motivo:</strong><br>
                                            {reason or 'Motivo não informado'}
                                        </p>
                                    </div>
        """ if reason else ""

        text = (
            f"Olá,\n\n"
            f"Agradecemos o interesse da ONG {org_name} em fazer parte do Instituto Impacto Social.\n\n"
            f"O Instituto Impacto Social é uma plataforma digital que facilita o acesso a serviços públicos "
            f"para pessoas trans, utilizando IA para recomendar serviços como retificação de documentos, "
            f"atendimento no SUS, programas sociais e apoio psicossocial.\n\n"
            f"Após análise cuidadosa, sua solicitação não foi aprovada no momento.\n"
            f"{reason_text}\n"
            f"O que fazer agora:\n"
            f"- Revise as informações cadastradas\n"
            f"- Faça os ajustes necessários\n"
            f"- Envie uma nova solicitação quando estiver preparade\n\n"
            "Estamos à disposição para esclarecer dúvidas e ajudar no processo.\n"
        )
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Análise da ONG - {org_name}</title>
        </head>
        <body style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;background-color:#f4f4f7;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f7;padding:40px 20px;">
                <tr>
                    <td align="center">
                        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background-color:#ffffff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.05);overflow:hidden;">
                            <!-- Header -->
                            <tr>
                                <td style="background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);padding:40px 30px;text-align:center;">
                                    <div style="width:64px;height:64px;background-color:rgba(255,255,255,0.2);border-radius:50%;margin:0 auto 20px;display:flex;align-items:center;justify-content:center;">
                                        <div style="font-size:40px;">ℹ</div>
                                    </div>
                                    <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:700;letter-spacing:-0.5px;">
                                        Análise da Solicitação
                                    </h1>
                                </td>
                            </tr>

                            <!-- Content -->
                            <tr>
                                <td style="padding:40px 30px;">
                                    <h2 style="margin:0 0 20px;color:#1a202c;font-size:24px;font-weight:600;text-align:center;">
                                        Análise da Solicitação
                                    </h2>
                                    <p style="margin:0 0 24px;color:#4a5568;font-size:16px;line-height:1.6;">
                                        Agradecemos o interesse da ONG <strong style="color:#f59e0b;">{org_name}</strong> em fazer parte do Instituto Impacto Social.
                                    </p>

                                    <!-- About Platform Box -->
                                    <div style="background-color:#f8f9ff;border-left:4px solid #667eea;border-radius:8px;padding:20px;margin:0 0 24px;">
                                        <p style="margin:0 0 12px;color:#1a202c;font-size:15px;font-weight:600;">
                                            Sobre a plataforma:
                                        </p>
                                        <p style="margin:0;color:#4a5568;font-size:14px;line-height:1.6;">
                                            O Instituto Impacto Social é uma plataforma digital que facilita o acesso a serviços públicos para <strong>pessoas trans</strong>, utilizando IA para recomendar serviços como retificação de documentos, atendimento no SUS, programas sociais e apoio psicossocial.
                                        </p>
                                    </div>

                                    <p style="margin:0 0 24px;color:#4a5568;font-size:16px;line-height:1.6;">
                                        Após análise cuidadosa, sua solicitação não foi aprovada no momento.
                                    </p>

                                    {reason_html}

                                    <!-- Info Box -->
                                    <div style="background-color:#fffbeb;border-left:4px solid #f59e0b;border-radius:8px;padding:20px;margin:0 0 24px;">
                                        <p style="margin:0 0 12px;color:#92400e;font-size:15px;font-weight:600;">
                                            O que fazer agora:
                                        </p>
                                        <ul style="margin:0;padding-left:20px;color:#92400e;font-size:14px;line-height:1.8;">
                                            <li>Revise as informações cadastradas</li>
                                            <li>Faça os ajustes necessários</li>
                                            <li>Envie uma nova solicitação quando estiver preparade</li>
                                        </ul>
                                    </div>

                                    <p style="margin:0;color:#718096;font-size:14px;line-height:1.6;text-align:center;">
                                        Estamos à disposição para esclarecer dúvidas e ajudar no processo.
                                    </p>
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="background-color:#f7fafc;padding:30px;text-align:center;border-top:1px solid #e2e8f0;">
                                    <p style="margin:0 0 8px;color:#718096;font-size:13px;">
                                        Instituto Impacto Social
                                    </p>
                                    <p style="margin:0;color:#a0aec0;font-size:12px;">
                                        Transformando vidas através da solidariedade
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    email_service.send_email(subject, recipient, text_body=text, html_body=html)
