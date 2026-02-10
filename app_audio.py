import streamlit as st
import os
import time
import wave
from google import genai
from google.genai import types

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Fábrica 9.3 - Director's Cut", layout="wide", page_icon="🎬")
st.title("🎬 Fábrica 9.3 - Ajuste Fino de Vozes")
st.markdown("---")

# --- FUNÇÕES ---
def carregar_arquivo(caminho):
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f: return f.read()
    return ""

def salvar_arquivo(caminho, conteudo):
    with open(caminho, "w", encoding="utf-8") as f: f.write(conteudo)

def ler_capitulos_pasta(pasta):
    conteudo, arqs = "", []
    if not os.path.exists(pasta): os.makedirs(pasta)
    for f in sorted(os.listdir(pasta)):
        if f.endswith(".md") or f.endswith(".txt"):
            with open(os.path.join(pasta, f), "r", encoding="utf-8") as file:
                texto = file.read()
                conteudo += f"\n--- {f} ---\n{texto}\n"
                arqs.append(f)
    return conteudo, arqs

def quebrar_texto_seguro(texto, limite_chars=800): 
    paragrafos = texto.split('\n')
    blocos = []
    bloco_atual = ""
    for p in paragrafos:
        if len(bloco_atual) + len(p) > limite_chars:
            if bloco_atual: blocos.append(bloco_atual)
            bloco_atual = p + "\n"
        else:
            bloco_atual += p + "\n"
    if bloco_atual: blocos.append(bloco_atual)
    return blocos

# --- GERENCIAMENTO DE CHAVES ---
if "lista_chaves" not in st.session_state:
    st.session_state["lista_chaves"] = carregar_arquivo("chaves_todas.txt")
if "indice_chave_atual" not in st.session_state:
    st.session_state["indice_chave_atual"] = 0

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🔑 Cofre de Chaves")
    input_chaves = st.text_area("Lista de API Keys:", value=st.session_state["lista_chaves"], height=150)
    
    if input_chaves != st.session_state["lista_chaves"]:
        st.session_state["lista_chaves"] = input_chaves
        salvar_arquivo("chaves_todas.txt", input_chaves)
        st.session_state["indice_chave_atual"] = 0 
        st.success("Chaves salvas!")

    chaves_limpas = [k.strip() for k in input_chaves.split('\n') if k.strip()]
    st.write(f"🗝️ Usando Chave {st.session_state['indice_chave_atual'] + 1}")

    st.markdown("---")
    st.header("🎙️ Elenco")
    voz_narradora = st.selectbox("Speaker 1 (Narradora/Ela)", ["Sulafat", "Kore"], index=0)
    voz_ele = st.selectbox("Speaker 2 (Ele)", ["Charon", "Puck", "Fenrir"], index=0)

# --- ABAS PRINCIPAIS ---
tab1, tab2, tab3, tab4 = st.tabs(["🧠 Cérebro", "✍️ Texto", "🎬 Roteiro (Diretor)", "🎧 Gravação"])

# === ABA 1: CÉREBRO ===
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📜 Bíblia")
        biblia = st.text_area("Personagens e Trama:", value=carregar_arquivo("biblia.txt"), height=400)
        if st.button("Salvar Bíblia"): salvar_arquivo("biblia.txt", biblia)
    with c2:
        st.subheader("📚 Capítulos")
        ctx, arqs = ler_capitulos_pasta("meus_capitulos")
        if arqs: 
            st.success(f"{len(arqs)} capítulos encontrados.")
            st.text_area("Contexto:", value=ctx, height=300, disabled=True)

# === ABA 2: ESCRITA ===
with tab2:
    st.header("✨ Texto Literário")
    with st.expander("🤖 Gerar Novo Capítulo"):
        briefing = st.text_area("O que acontece agora?", height=80)
        if st.button("🚀 Escrever"):
            if not chaves_limpas: st.error("Falta chave!")
            else:
                with st.spinner("Escrevendo..."):
                    try:
                        chave = chaves_limpas[st.session_state["indice_chave_atual"]]
                        client = genai.Client(api_key=chave)
                        prompt = f"""Atue como escritora.
                        BÍBLIA: {biblia}
                        CTX: {ctx}
                        BRIEFING: {briefing}
                        Escreva um capítulo."""
                        resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                        st.session_state['texto_literario'] = resp.text
                        st.rerun()
                    except Exception as e: st.error(f"Erro: {e}")

    if 'texto_literario' not in st.session_state: st.session_state['texto_literario'] = ""
    texto_literario = st.text_area("Seu Texto:", value=st.session_state['texto_literario'], height=500)
    st.session_state['texto_literario'] = texto_literario

# === ABA 3: ROTEIRO (AQUI ESTÁ A MÁGICA) ===
with tab3:
    st.header("🎬 Roteiro (Ajuste de POV)")
    st.info("O Diretor agora entende que a Narradora lê as tags 'disse ele'.")
    
    if st.button("🎭 Gerar Roteiro (Primeira Pessoa)"):
        if not texto_literario: st.warning("Sem texto!")
        elif not chaves_limpas: st.error("Sem chaves!")
        else:
            with st.spinner("O Diretor está separando as vozes..."):
                try:
                    chave = chaves_limpas[st.session_state["indice_chave_atual"]]
                    client = genai.Client(api_key=chave)
                    
                    # --- PROMPT REVISADO PARA 1ª PESSOA ---
                    prompt = f"""
                    Aja como um DIRETOR DE DUBLAGEM Meticuloso.
                    O livro é narrado em PRIMEIRA PESSOA pela protagonista feminina (Speaker 1).
                    
                    REGRAS DE OURO PARA A DIVISÃO DE VOZES:
                    
                    1. SPEAKER 1 (NARRADORA/ELA):
                       - Lê toda a narração e descrições.
                       - Lê os pensamentos dela.
                       - Lê as falas dela.
                       - Lê AS TAGS DE DIÁLOGO DELE (ex: "... - ele disse", "... - gritou ele", "... - ele respondeu").
                    
                    2. SPEAKER 2 (ELE):
                       - Lê APENAS e EXCLUSIVAMENTE a voz falada dele (o conteúdo do diálogo entre aspas ou travessão).
                       - NÃO deve ler "ele disse", "ele riu", "ele sussurrou". Isso pertence à narradora.
                    
                    EXEMPLO DE COMO FAZER:
                    Texto Original: "- Oi, como você está? - ele perguntou, sorrindo."
                    
                    Seu Roteiro:
                    Speaker 2: (warmly) - Oi, como você está?
                    Speaker 1: - ele perguntou, sorrindo.
                    
                    TEXTO PARA ROTEIRIZAR:
                    {texto_literario}
                    """
                    
                    resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                    st.session_state['roteiro_final'] = resp.text
                    st.rerun()
                except Exception as e: st.error(f"Erro: {e}")
    
    roteiro = st.text_area("Roteiro Final:", value=st.session_state.get('roteiro_final', ''), height=600)
    st.session_state['roteiro_final'] = roteiro

# === ABA 4: GRAVAÇÃO ===
with tab4:
    st.header("🎧 Gravação")
    if st.button("🎙️ Iniciar Gravação"):
        if not roteiro or not chaves_limpas:
            st.error("Falta Roteiro ou Chaves!")
        else:
            caminho_pasta = os.path.abspath("audios_gemini")
            if not os.path.exists(caminho_pasta): os.makedirs(caminho_pasta)
            
            for f in os.listdir(caminho_pasta):
                try: os.remove(os.path.join(caminho_pasta, f))
                except: pass

            blocos = quebrar_texto_seguro(roteiro, limite_chars=800)
            progress = st.progress(0)
            status = st.empty()

            for i, bloco in enumerate(blocos):
                sucesso = False
                tentativas = 0
                max_trocas = len(chaves_limpas)
                
                while not sucesso and tentativas < max_trocas:
                    idx = st.session_state["indice_chave_atual"]
                    chave_atual = chaves_limpas[idx]
                    status.markdown(f"🔴 **Gravando Cena {i+1}/{len(blocos)}** (Chave {idx+1})...")
                    
                    try:
                        client = genai.Client(api_key=chave_atual)
                        prompt_audio = f"""Perform dramatically. 
                        Voices: Speaker 1={voz_narradora}, Speaker 2={voz_ele}. 
                        Script: {bloco}"""
                        
                        config = types.GenerateContentConfig(
                            temperature=1, response_modalities=["audio"],
                            speech_config=types.SpeechConfig(
                                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                                    speaker_voice_configs=[
                                        types.SpeakerVoiceConfig(speaker="Speaker 1", voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voz_narradora))),
                                        types.SpeakerVoiceConfig(speaker="Speaker 2", voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voz_ele))),
                                    ])))

                        audio_buffer = bytearray()
                        
                        for chunk in client.models.generate_content_stream(
                            model="gemini-2.5-pro-preview-tts",
                            contents=[types.Content(parts=[types.Part.from_text(text=prompt_audio)])],
                            config=config,
                        ):
                            if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                                part = chunk.candidates[0].content.parts[0]
                                if part.inline_data: 
                                    audio_buffer.extend(part.inline_data.data)
                        
                        if len(audio_buffer) > 0:
                            path = os.path.join(caminho_pasta, f"parte_{i+1:03d}.wav")
                            with wave.open(path, 'wb') as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(24000)
                                wf.writeframes(audio_buffer)
                            st.audio(path)
                            sucesso = True
                        else: 
                            raise Exception("Áudio vazio")
                        
                        if i < len(blocos) - 1: time.sleep(25)

                    except Exception as e:
                        erro = str(e)
                        if "429" in erro or "RESOURCE" in erro or "500" in erro or "vazio" in erro:
                            st.warning(f"⚠️ Erro na Chave {idx+1}. Trocando...")
                            st.session_state["indice_chave_atual"] = (idx + 1) % len(chaves_limpas)
                            tentativas += 1
                            time.sleep(3)
                        else:
                            st.error(f"Erro fatal: {e}")
                            break
                
                if not sucesso: break
                progress.progress((i+1)/len(blocos))
            
            if sucesso:
                st.success("✅ Feito!")
                st.balloons()
                if st.button("Abrir Pasta"): os.startfile(caminho_pasta)