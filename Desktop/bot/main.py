import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, ContextTypes, filters
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAZIONE BOT - INSERISCI QUI I TUOI DATI
# ═══════════════════════════════════════════════════════════════════════════════

TOKEN = "8038621677:AAG29CD26RGucbmq1qAPgJk5jaMCcYO0aqk"
WEBHOOK_URL = "https://vburrosbot.vercel.app/webhook"

GROUP_ID_LOG = -1003241826633

GROUP_ID_DIREZIONE = -1002907363855
GROUP_ID_PROPAGANDA = -1002608247986
GROUP_ID_EVENTI = -1001234567892
GROUP_ID_GRAFICA = -1001234567893

GRUPPO_DESTINAZIONE = {
    "Info generali": [GROUP_ID_DIREZIONE, GROUP_ID_PROPAGANDA, GROUP_ID_EVENTI, GROUP_ID_GRAFICA],
    "Supporto sussidi": [GROUP_ID_DIREZIONE, GROUP_ID_PROPAGANDA],
    "Proposte": [GROUP_ID_DIREZIONE, GROUP_ID_PROPAGANDA, GROUP_ID_EVENTI, GROUP_ID_GRAFICA],
    "Segnalazione": [GROUP_ID_DIREZIONE]
}

LINK_DIVENTA_MEMBRO = "https://forms.gle/ycUZ5XcmnKSgNUwc9"
LINK_RICHIEDI_SUSSIDI = "https://forms.gle/XFvBM6Q9AKJPuPfK8"

MESSAGGIO_BENVENUTO = """
<b>👋 Benvenuto/a nel bot del partito Giustizia d'Impero!</b>

Per ogni richiesta sono qui ad aiutarti
Usa i pulsanti qui sotto per navigare nel menu.
"""

TESTO_PRE_LINK_MEMBRO = """
<b>🪪 Diventa Membro</b>

Per unirti alla nostra organizzazione, clicca sul link qui sotto:
"""

TESTO_POST_LINK_MEMBRO = """
Compila il form per completare la registrazione!
"""

MESSAGGIO_SUSSIDI = """
<b>GIUSTIZIA D'IMPERIO — SUSSIDI E AIUTI SOCIALI</b>

Sussidi richiedibili <u>SOLO UNA VOLTA</u>:

<blockquote>📕 Sussidio Scolastico</blockquote>
• Rimborso per <u>5 servizi</u> dell'Istituto "Giovanni Gentile".
Tra i servizi ci sono:
   - Recupero di un voto;
   - Corso di formazione;
   - Corso serale (esclusivo dei lavoratori di aziende statali).
<u><i>N.b.</i></u> 
<u><i>Il sussidio non è valido ai fini dello svolgimento dell'Esame di Maturità da privatista.</i></u> 


<blockquote>🎓 Sussidio Universitario</blockquote>
• Rimborso presso Università "Santa Helenie" <u>fino a 4.000€</u> delle spese universitarie (tasse, libri, materiali).


<blockquote>🏠 Sussidio Alloggio</blockquote>
• <u>Alloggio gratuito</u> in hotel convenzionato con il Partito dotato di casse personali in cui custodire i propri oggetti personali e di valore.


<blockquote>👶🏼 Sussidio Pipino</blockquote>
• <u>1 telefono</u> "ferro";
• <u>5 asce</u> o <u>picconi</u>;
• <u>1 zaino personale</u> a 18 slot per trasporto risorse.


Altri aiuti:

<blockquote>🍔 Assistenza viveri</blockquote>
Sei a corto di cibo o bevande? Non preoccuparti, dicci qual è il tuo cibo preferito e avrai uno <u>sconto del 50%</u> presso <u>CapyBar</u> sul menù GI (che comprende uno stack tuo cibo preferito e uno di acqua). 
<i>⏱️ Disponibilità aiuto: 1 volta a settimana</i>


<blockquote>📜 Assistenza CV</blockquote>
Non hai idea di come impostare il tuo Curriculum Vitae?
Non preoccuparti, basta chiedere una mano, qualcuno ti risponderà subito per chiarire ogni dubbio e aiutarti ad impostare il tuo CV perfetto.
<i>✅ Disponibilità aiuto: perenne</i>


<blockquote>⚖️ Assistenza Legale</blockquote>
Hai problemi con la legge? 
Uno dei nostri avvocati provvederà <u>in modo totalmente gratuito</u> a fornirti un'<u>assistenza legale professionale</u>. 
<i>✅ Disponibilità aiuto: perenne</i>


<blockquote>💊 Emergenza medica</blockquote>
Ti sei fatto/a male? Ti sei bruciato/a? Preoccupato/a per i virus in circolazione?
Niente paura! <u>Cerotti, pomate e mascherine</u> ti verranno forniti sempre <u>gratuitamente</u>, basta chiedere a noi! 
<i>✅ Disponibilità aiuto: perenne</i>



❓ Come accedo ai sussidi?
• Presenta la tua richiesta del sussidio che preferisci, puoi farlo:
     - in sede centrale;
     - tramite modulo online.
• Verificheremo i requisiti economici e statutari.
• In caso di approvazione dei requisiti ti verrà fornito il sussidio nel minor tempo possibile.


<u><b>⚠️ ATTENZIONE ⚠️</b></u>
<u><b>IL CAMBIO DI PARTITO, O L'USCITA DA QUEST'ULTIMO SONO FATTORI DETERMINANTI CHE CAUSERANNO LA REVOCA TOTALE DI QUESTI SUSSIDI.</b></u>


<blockquote><b>📢 CONTATTI UFFICIALI</b>
🤖 Bot Telegram: @GiustiziaImpero_BOT
📍Sede NeoTecno: -816 65 172
</blockquote>

<b><i>GIUSTIZIA D'IMPERIO</i></b>
<blockquote><i>Solo chi lotta per la giustizia costruisce un futuro di speranza</i></blockquote>

<u>🤵🏽 Presidente:</u>
<u>nubelluwaju</u>

<u>🤵🏽 Vice Presidente:</u>
<u>PuskaMillennium</u>


<u>Per richiedere i sussidi, usa il pulsante qui sotto.</u>
"""

LISTA_DIREZIONE = """
🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 
Siamo in attesa dell'approvazione dello statuto, appena ce lo approveranno scriveremo tutti i ruoli completi. 
Ci scusiamo per il disagio.❤️
🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧
"""

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAZIONE LOGGING
# ═══════════════════════════════════════════════════════════════════════════════
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# STATI CONVERSAZIONALI
# ═══════════════════════════════════════════════════════════════════════════════
INIZIO, MOTIVO, NICKNAME_MC, SPIEGAZIONE, CONFERMA, SCELTA_MODIFICA = range(6)

# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════════════════
app = FastAPI()
application = None


# ═══════════════════════════════════════════════════════════════════════════════
# FUNZIONI UTILITY
# ═══════════════════════════════════════════════════════════════════════════════

def get_timestamp():
    """Restituisce data e ora formattate per il logging"""
    now = datetime.now()
    data = now.strftime("%d/%m/%Y")
    ora = now.strftime("%H:%M:%S")
    return data, ora


async def log_azione(context: ContextTypes.DEFAULT_TYPE, intestazione: str,
                     user_id: int, username: str, azione: str, extra: str = ""):
    """Invia un messaggio di log al gruppo log"""
    data, ora = get_timestamp()

    messaggio_log = f"""
{intestazione}

👤 <b>Username:</b> @{username if username else 'Non disponibile'}
🆔 <b>User ID:</b> {user_id}
📅 <b>Data:</b> {data}
⏰ <b>Ora:</b> {ora}
📝 <b>Azione:</b> {azione}
{extra}
"""

    try:
        await context.bot.send_message(
            chat_id=GROUP_ID_LOG,
            text=messaggio_log,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Errore invio log: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# MENU PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════

def main_menu_keyboard():
    """Crea la tastiera del menu principale"""
    keyboard = [
        [InlineKeyboardButton("🪪 Diventa membro", callback_data="diventa_membro")],
        [InlineKeyboardButton("🏷️ I tuoi sussidi", callback_data="sussidi")],
        [InlineKeyboardButton("⚖️ Direzione GI", callback_data="direzione")],
        [InlineKeyboardButton("❓ Richiesta direzione", callback_data="richiesta_direzione")],
        [InlineKeyboardButton("⚠️ Problemi col bot", callback_data="problemi_bot")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Comando /start - Mostra il menu principale"""
    user = update.effective_user

    await log_azione(
        context,
        "🚀 AVVIO BOT",
        user.id,
        user.username,
        "Comando /start eseguito"
    )

    messaggio_personalizzato = f"""
<b>👋 Benvenuto {user.first_name}!</b>

Per ogni richiesta sono qui ad aiutarti
Usa i pulsanti qui sotto per navigare nel menu.
"""

    await update.message.reply_text(
        messaggio_personalizzato,
        reply_markup=main_menu_keyboard(),
        parse_mode='HTML'
    )

    return INIZIO


# ═══════════════════════════════════════════════════════════════════════════════
# SEZIONE: DIVENTA MEMBRO
# ═══════════════════════════════════════════════════════════════════════════════

async def diventa_membro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra informazioni per diventare membro"""
    query = update.callback_query
    await query.answer()
    user = query.from_user

    await log_azione(
        context,
        "🪪🪪🪪 Diventa membro 🪪🪪🪪",
        user.id,
        user.username,
        "Visualizzazione info iscrizione"
    )

    messaggio = f"""{TESTO_PRE_LINK_MEMBRO}

<a href="{LINK_DIVENTA_MEMBRO}">🔗 Clicca qui per iscriverti</a>

{TESTO_POST_LINK_MEMBRO}"""

    keyboard = [[InlineKeyboardButton("↩️ Indietro", callback_data="torna_menu")]]

    await query.edit_message_text(
        messaggio,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    return INIZIO


# ═══════════════════════════════════════════════════════════════════════════════
# SEZIONE: I TUOI SUSSIDI
# ═══════════════════════════════════════════════════════════════════════════════

async def sussidi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra informazioni sui sussidi"""
    query = update.callback_query
    await query.answer()
    user = query.from_user

    await log_azione(
        context,
        "🏷️🏷️🏷️ I tuoi sussidi 🏷️🏷️🏷️",
        user.id,
        user.username,
        "Visualizzazione sussidi"
    )

    keyboard = [
        [InlineKeyboardButton("📋 Richiedi sussidi", url=LINK_RICHIEDI_SUSSIDI)],
        [InlineKeyboardButton("↩️ Indietro", callback_data="torna_menu")]
    ]

    await query.edit_message_text(
        MESSAGGIO_SUSSIDI,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    return INIZIO


# ═══════════════════════════════════════════════════════════════════════════════
# SEZIONE: DIREZIONE GI
# ═══════════════════════════════════════════════════════════════════════════════

async def direzione(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra la lista dei membri della direzione"""
    query = update.callback_query
    await query.answer()
    user = query.from_user

    await log_azione(
        context,
        "⚖️⚖️⚖️ Direzione GI ⚖️⚖️⚖️",
        user.id,
        user.username,
        "Visualizzazione direzione"
    )

    keyboard = [[InlineKeyboardButton("↩️ Indietro", callback_data="torna_menu")]]

    await query.edit_message_text(
        LISTA_DIREZIONE,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    return INIZIO


# ═══════════════════════════════════════════════════════════════════════════════
# SEZIONE: PROBLEMI COL BOT
# ═══════════════════════════════════════════════════════════════════════════════

async def problemi_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra informazioni per supporto tecnico"""
    query = update.callback_query
    await query.answer()
    user = query.from_user

    await log_azione(
        context,
        "⚠️⚠️⚠️ Problemi col bot ⚠️⚠️⚠️",
        user.id,
        user.username,
        "Richiesta supporto tecnico"
    )

    messaggio = """
<b>🆘 Supporto Tecnico</b>

Se riscontri qualche problema con il bot o hai suggerimenti, 
scrivi a <b>@gianspizza</b>.
"""

    keyboard = [[InlineKeyboardButton("↩️ Indietro", callback_data="torna_menu")]]

    await query.edit_message_text(
        messaggio,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    return INIZIO


# ═══════════════════════════════════════════════════════════════════════════════
# SEZIONE: RICHIESTA DIREZIONE - STATO 1 (Scegli Motivo)
# ═══════════════════════════════════════════════════════════════════════════════

async def richiesta_direzione_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Avvia il processo di richiesta alla direzione"""
    query = update.callback_query
    await query.answer()
    user = query.from_user

    context.user_data.clear()

    await log_azione(
        context,
        "❓❓❓ Richiesta direzione ❓❓❓",
        user.id,
        user.username,
        "Avvio processo richiesta"
    )

    keyboard = [
        [InlineKeyboardButton("Info generali", callback_data="motivo_info_generali")],
        [InlineKeyboardButton("Supporto sussidi", callback_data="motivo_supporto_sussidi")],
        [InlineKeyboardButton("Proposte", callback_data="motivo_proposte")],
        [InlineKeyboardButton("Segnalazione", callback_data="motivo_segnalazione")],
        [InlineKeyboardButton("↩️ Indietro", callback_data="torna_menu")]
    ]

    await query.edit_message_text(
        "<b>❓ Richiesta Direzione</b>\n\nHai bisogno di aiuto? Scegli la categoria:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    return MOTIVO


async def motivo_scelto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Salva il motivo scelto e chiede il nickname Minecraft"""
    query = update.callback_query
    await query.answer()
    user = query.from_user

    motivo_mapping = {
        "motivo_info_generali": "Info generali",
        "motivo_supporto_sussidi": "Supporto sussidi",
        "motivo_proposte": "Proposte",
        "motivo_segnalazione": "Segnalazione"
    }

    motivo = motivo_mapping.get(query.data)
    context.user_data['motivo'] = motivo
    context.user_data['username_telegram'] = user.username if user.username else "Non disponibile"
    context.user_data['user_id'] = user.id

    gruppi_dest = GRUPPO_DESTINAZIONE[motivo]
    gruppi_str = ", ".join(str(g) for g in gruppi_dest)
    await log_azione(
        context,
        "❓❓❓ Richiesta direzione ❓❓❓",
        user.id,
        user.username,
        f"Motivo selezionato: {motivo}",
        f"📍 <b>Gruppi destinazione:</b> {gruppi_str}"
    )

    keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data="annulla_richiesta")]]

    await query.edit_message_text(
        "<b>🖥️ Nickname Minecraft</b>\n\nInserisci il tuo nickname su Minecraft:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    return NICKNAME_MC


# ═══════════════════════════════════════════════════════════════════════════════
# SEZIONE: RICHIESTA DIREZIONE - STATO 2 (Nickname Minecraft)
# ═══════════════════════════════════════════════════════════════════════════════

async def nickname_inserito(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Salva il nickname e chiede la spiegazione"""
    nickname = update.message.text
    user = update.effective_user

    context.user_data['nickname_minecraft'] = nickname

    await log_azione(
        context,
        "❓❓❓ Richiesta direzione ❓❓❓",
        user.id,
        user.username,
        "Nickname Minecraft inserito",
        f"🖥️ <b>Nickname:</b> {nickname}"
    )

    keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data="annulla_richiesta")]]

    await update.message.reply_text(
        "<b>❓ Spiegazione Richiesta</b>\n\nSpiega la tua richiesta in dettaglio:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    return SPIEGAZIONE


# ═══════════════════════════════════════════════════════════════════════════════
# SEZIONE: RICHIESTA DIREZIONE - STATO 3 (Spiegazione)
# ═══════════════════════════════════════════════════════════════════════════════

async def spiegazione_inserita(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Salva la spiegazione e mostra il resoconto"""
    spiegazione = update.message.text
    user = update.effective_user

    context.user_data['spiegazione'] = spiegazione

    await log_azione(
        context,
        "❓❓❓ Richiesta direzione ❓❓❓",
        user.id,
        user.username,
        "Spiegazione inserita",
        f"❓ <b>Spiegazione:</b> {spiegazione[:100]}..."
    )

    return await mostra_resoconto(update, context)


async def mostra_resoconto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra il resoconto della richiesta per conferma"""
    dati = context.user_data

    resoconto = f"""
<b>📋 RIEPILOGO RICHIESTA</b>

👤 <b>Utente:</b> @{dati['username_telegram']}
🖥️ <b>Minecraft:</b> {dati['nickname_minecraft']}
💬 <b>Motivazione:</b> {dati['motivo']}
❓ <b>Spiegazione:</b> {dati['spiegazione']}
"""

    keyboard = [
        [InlineKeyboardButton("✅ Conferma", callback_data="conferma_richiesta")],
        [InlineKeyboardButton("🔄 Modifica", callback_data="modifica_richiesta")],
        [InlineKeyboardButton("❌ Annulla", callback_data="annulla_richiesta")]
    ]

    if update.callback_query:
        await update.callback_query.edit_message_text(
            resoconto,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            resoconto,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    return CONFERMA


# ═══════════════════════════════════════════════════════════════════════════════
# SEZIONE: RICHIESTA DIREZIONE - STATO 4 (Conferma)
# ═══════════════════════════════════════════════════════════════════════════════

async def conferma_richiesta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Invia la richiesta ai gruppi specifici in base al motivo"""
    query = update.callback_query
    await query.answer()
    user = query.from_user

    dati = context.user_data
    motivo = dati['motivo']
    gruppi_destinazione = GRUPPO_DESTINAZIONE[motivo]

    messaggio_gruppo = f"""
<b>📩 NUOVA RICHIESTA</b>

👤 <b>Utente:</b> @{dati['username_telegram']}
🖥️ <b>Minecraft:</b> {dati['nickname_minecraft']}
💬 <b>Motivazione:</b> {motivo}
❓ <b>Spiegazione:</b> {dati['spiegazione']}
"""

    keyboard_gruppo = [
        [InlineKeyboardButton("✅ Accetta richiesta",
                              callback_data=f"accetta_{dati['user_id']}")]
    ]

    try:
        for gruppo_id in gruppi_destinazione:
            await context.bot.send_message(
                chat_id=gruppo_id,
                text=messaggio_gruppo,
                reply_markup=InlineKeyboardMarkup(keyboard_gruppo),
                parse_mode='HTML'
            )

        gruppi_str = ", ".join(str(g) for g in gruppi_destinazione)
        await log_azione(
            context,
            "❓❓❓ Richiesta direzione ❓❓❓",
            user.id,
            user.username,
            "Richiesta confermata e inviata",
            f"💬 <b>Motivo:</b> {motivo}\n📍 <b>Gruppi:</b> {gruppi_str}"
        )

        await query.edit_message_text(
            "<b>✅ Richiesta Inviata!</b>\n\nLa tua richiesta è stata inviata alla direzione. "
            "Riceverai una notifica quando verrà presa in carico.",
            parse_mode='HTML'
        )

        await asyncio.sleep(2)
        await query.message.reply_text(
            MESSAGGIO_BENVENUTO,
            reply_markup=main_menu_keyboard(),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Errore invio richiesta: {e}")
        await query.edit_message_text(
            "<b>❌ Errore</b>\n\nC'è stato un problema nell'invio della richiesta. Riprova più tardi.\nSe l'errore persiste contattare @gianspizza.",
            parse_mode='HTML'
        )

    context.user_data.clear()

    return INIZIO


# ═══════════════════════════════════════════════════════════════════════════════
# SEZIONE: RICHIESTA DIREZIONE - MODIFICA DATI
# ═══════════════════════════════════════════════════════════════════════════════

async def modifica_richiesta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra il menu di modifica"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("💬 Motivo", callback_data="modifica_motivo")],
        [InlineKeyboardButton("🖥️ Nick Minecraft", callback_data="modifica_nickname")],
        [InlineKeyboardButton("❓ Spiegazione", callback_data="modifica_spiegazione")],
        [InlineKeyboardButton("↩️ Indietro", callback_data="torna_conferma")]
    ]

    await query.edit_message_text(
        "<b>🔄 Modifica Richiesta</b>\n\nCosa vuoi modificare?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    return SCELTA_MODIFICA


async def modifica_campo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gestisce la modifica di un campo specifico"""
    query = update.callback_query
    await query.answer()

    campo = query.data.replace("modifica_", "")
    context.user_data['campo_in_modifica'] = campo

    if campo == "motivo":
        keyboard = [
            [InlineKeyboardButton("Info generali", callback_data="motivo_info_generali")],
            [InlineKeyboardButton("Supporto sussidi", callback_data="motivo_supporto_sussidi")],
            [InlineKeyboardButton("Proposte", callback_data="motivo_proposte")],
            [InlineKeyboardButton("Segnalazione", callback_data="motivo_segnalazione")],
            [InlineKeyboardButton("↩️ Indietro", callback_data="torna_conferma")]
        ]
        await query.edit_message_text(
            "<b>💬 Modifica Motivo</b>\n\nScegli il nuovo motivo:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return MOTIVO

    elif campo == "nickname":
        keyboard = [[InlineKeyboardButton("↩️ Indietro", callback_data="torna_conferma")]]
        await query.edit_message_text(
            "<b>🖥️ Modifica Nickname</b>\n\nInserisci il nuovo nickname Minecraft:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return NICKNAME_MC

    elif campo == "spiegazione":
        keyboard = [[InlineKeyboardButton("↩️ Indietro", callback_data="torna_conferma")]]
        await query.edit_message_text(
            "<b>❓ Modifica Spiegazione</b>\n\nInserisci la nuova spiegazione:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return SPIEGAZIONE


async def torna_conferma(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Torna al resoconto di conferma"""
    query = update.callback_query
    await query.answer()

    context.user_data.pop('campo_in_modifica', None)

    dati = context.user_data

    resoconto = f"""
<b>📋 RIEPILOGO RICHIESTA</b>

👤 <b>Utente:</b> @{dati['username_telegram']}
🖥️ <b>Minecraft:</b> {dati['nickname_minecraft']}
💬 <b>Motivazione:</b> {dati['motivo']}
❓ <b>Spiegazione:</b> {dati['spiegazione']}
"""

    keyboard = [
        [InlineKeyboardButton("✅ Conferma", callback_data="conferma_richiesta")],
        [InlineKeyboardButton("🔄 Modifica", callback_data="modifica_richiesta")],
        [InlineKeyboardButton("❌ Annulla", callback_data="annulla_richiesta")]
    ]

    await query.edit_message_text(
        resoconto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    return CONFERMA


# ═══════════════════════════════════════════════════════════════════════════════
# SEZIONE: ANNULLA RICHIESTA
# ═══════════════════════════════════════════════════════════════════════════════

async def annulla_richiesta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Annulla la richiesta e torna al menu principale"""
    query = update.callback_query
    await query.answer()
    user = query.from_user

    await log_azione(
        context,
        "❓❓❓ Richiesta direzione ❓❓❓",
        user.id,
        user.username,
        "Richiesta annullata dall'utente"
    )

    context.user_data.clear()

    await query.edit_message_text(
        MESSAGGIO_BENVENUTO,
        reply_markup=main_menu_keyboard(),
        parse_mode='HTML'
    )

    return INIZIO


# ═══════════════════════════════════════════════════════════════════════════════
# SEZIONE: ACCETTAZIONE RICHIESTA
# ═══════════════════════════════════════════════════════════════════════════════

async def accetta_richiesta_direzione(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce l'accettazione della richiesta da parte di un membro direzione"""
    query = update.callback_query
    await query.answer("Richiesta accettata!")

    membro_direzione = query.from_user
    user_id_richiedente = int(query.data.replace("accetta_", ""))

    try:
        messaggio_notifica = f"""
<b>✅ Richiesta Accettata</b>

@{membro_direzione.username if membro_direzione.username else 'Un membro della direzione'} ha accettato la tua richiesta.
Attendi la risposta!
"""

        await context.bot.send_message(
            chat_id=user_id_richiedente,
            text=messaggio_notifica,
            parse_mode='HTML'
        )

        await query.edit_message_text(
            query.message.text + f"\n\n<b>✅ Accettata da:</b> @{membro_direzione.username}",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🖋️ Rispondi alla richiesta",
                                      url=f"tg://user?id={user_id_richiedente}")]
            ])
        )

        await log_azione(
            context,
            "❓❓❓ Richiesta direzione ❓❓❓",
            membro_direzione.id,
            membro_direzione.username,
            f"Richiesta accettata da @{membro_direzione.username}",
            f"👤 <b>Utente richiedente ID:</b> {user_id_richiedente}"
        )

    except Exception as e:
        logger.error(f"Errore nell'accettazione richiesta: {e}")
        await query.edit_message_text(
            query.message.text + "\n\n<b>❌ Errore nell'invio della notifica</b>",
            parse_mode='HTML'
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TORNA AL MENU PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════

async def torna_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Torna al menu principale"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        MESSAGGIO_BENVENUTO,
        reply_markup=main_menu_keyboard(),
        parse_mode='HTML'
    )

    return INIZIO


# ═══════════════════════════════════════════════════════════════════════════════
# GESTIONE ERRORI
# ═══════════════════════════════════════════════════════════════════════════════

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gestisce la cancellazione della conversazione"""
    await update.message.reply_text(
        "Operazione annullata. Usa /start per ricominciare.",
        parse_mode='HTML'
    )
    context.user_data.clear()
    return ConversationHandler.END


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce gli errori"""
    logger.error(f"Errore: {context.error}")


# ═══════════════════════════════════════════════════════════════════════════════
# WEBHOOK ENDPOINT - VERCEL
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Endpoint webhook che riceve gli update da Telegram"""
    global application

    try:
        # Inizializza il bot al primo webhook
        if application is None:
            application = ApplicationBuilder().token(TOKEN).build()

            conv_handler = ConversationHandler(
                entry_points=[CommandHandler('start', start)],
                states={
                    INIZIO: [
                        CallbackQueryHandler(diventa_membro, pattern="^diventa_membro$"),
                        CallbackQueryHandler(sussidi, pattern="^sussidi$"),
                        CallbackQueryHandler(direzione, pattern="^direzione$"),
                        CallbackQueryHandler(richiesta_direzione_start, pattern="^richiesta_direzione$"),
                        CallbackQueryHandler(problemi_bot, pattern="^problemi_bot$"),
                        CallbackQueryHandler(torna_menu, pattern="^torna_menu$")
                    ],
                    MOTIVO: [
                        CallbackQueryHandler(motivo_scelto, pattern="^motivo_"),
                        CallbackQueryHandler(torna_menu, pattern="^torna_menu$"),
                        CallbackQueryHandler(torna_conferma, pattern="^torna_conferma$")
                    ],
                    NICKNAME_MC: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, nickname_inserito),
                        CallbackQueryHandler(annulla_richiesta, pattern="^annulla_richiesta$"),
                        CallbackQueryHandler(torna_conferma, pattern="^torna_conferma$")
                    ],
                    SPIEGAZIONE: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, spiegazione_inserita),
                        CallbackQueryHandler(annulla_richiesta, pattern="^annulla_richiesta$"),
                        CallbackQueryHandler(torna_conferma, pattern="^torna_conferma$")
                    ],
                    CONFERMA: [
                        CallbackQueryHandler(conferma_richiesta, pattern="^conferma_richiesta$"),
                        CallbackQueryHandler(modifica_richiesta, pattern="^modifica_richiesta$"),
                        CallbackQueryHandler(annulla_richiesta, pattern="^annulla_richiesta$")
                    ],
                    SCELTA_MODIFICA: [
                        CallbackQueryHandler(modifica_campo, pattern="^modifica_"),
                        CallbackQueryHandler(torna_conferma, pattern="^torna_conferma$")
                    ]
                },
                fallbacks=[CommandHandler('cancel', cancel)]
            )

            application.add_handler(conv_handler)
            application.add_handler(CallbackQueryHandler(accetta_richiesta_direzione, pattern="^accetta_"))
            application.add_error_handler(error_handler)

            logger.info("🤖 Bot inizializzato!")

        # Processa l'update
        update_data = await request.json()
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)

        return JSONResponse({"status": "ok"})

    except Exception as e:
        logger.error(f"Errore nel webhook: {e}")
        return JSONResponse({"status": "error", "message": str(e)})


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "Bot is running", "timestamp": datetime.now().isoformat()}

