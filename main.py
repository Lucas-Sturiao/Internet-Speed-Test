import tkinter as tk
import customtkinter as ctk
import speedtest
import threading
import csv
from datetime import datetime
import os

# Configurações visuais globais
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SpeedTestApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Internet Speed Test")
        self.geometry("700x450")
        self.resizable(False, False)

        # --- Título ---
        self.label_titulo = ctk.CTkLabel(self, text="SPEED TEST", font=("Roboto", 28, "bold"))
        self.label_titulo.pack(pady=30)

        # --- Container dos Cards ---
        self.frame_cards = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_cards.pack(fill="x", padx=40)

        # Card de Download
        self.card_down = self.criar_card("DOWNLOAD", "0.0", "#1f6aa5")
        self.card_down.grid(row=0, column=0, padx=10)

        # Card de Upload
        self.card_up = self.criar_card("UPLOAD", "0.0", "#2d8a4e")
        self.card_up.grid(row=0, column=1, padx=10)

        # Card de Latência (Ping)
        self.card_ping = self.criar_card("PING", "0", "#8e44ad")
        self.card_ping.grid(row=0, column=2, padx=10)

        # Configurar colunas iguais
        self.frame_cards.grid_columnconfigure((0, 1, 2), weight=1)

        # --- Status e Botão ---
        self.label_status = ctk.CTkLabel(self, text="Status: Pronto", font=("Roboto", 14))
        self.label_status.pack(pady=(40, 5))

        self.btn_start = ctk.CTkButton(self, text="START TEST", command=self.iniciar_thread_teste, width=200, height=50, font=("Roboto", 16, "bold"))
        self.btn_start.pack(pady=10)

        self.btn_hist = ctk.CTkButton(self, text="VER HISTÓRICO", command=self.abrir_historico, width=200, height=35, fg_color="transparent", border_width=2, text_color="white")
        self.btn_hist.pack(pady=5)

    def criar_card(self, titulo, valor_inicial, cor_destaque):
        # Frame do Card
        frame = ctk.CTkFrame(self.frame_cards, width=180, height=180, corner_radius=20)
        frame.pack_propagate(False) # Mantém o tamanho fixo
        
        lbl_titulo = ctk.CTkLabel(frame, text=titulo, font=("Roboto", 12, "bold"), text_color="gray")
        lbl_titulo.pack(pady=(20, 10))

        # O valor que será alterado
        lbl_valor = ctk.CTkLabel(frame, text=valor_inicial, font=("Roboto", 32, "bold"), text_color=cor_destaque)
        lbl_valor.pack(expand=True)

        lbl_unidade = ctk.CTkLabel(frame, text="Mbps" if titulo != "PING" else "ms", font=("Roboto", 10))
        lbl_unidade.pack(pady=(0, 20))

        # Atribui o label a uma variável para podermos atualizar depois
        if titulo == "DOWNLOAD": self.val_down = lbl_valor
        elif titulo == "UPLOAD": self.val_up = lbl_valor
        else: self.val_ping = lbl_valor
        
        return frame
    
    def salvar_historico(self, down, up, ping):
        # Pega a data e hora atual formatada
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Nome do arquivo
        arquivo = "historico.csv"
        
        # Verifica se o arquivo já existe para decidir se escreve o cabeçalho
        existe = os.path.exists(arquivo)
        
        with open(arquivo, mode="a", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            # Se o arquivo é novo, escreve os títulos das colunas
            if not existe:
                escritor.writerow(["Data/Hora", "Download (Mbps)", "Upload (Mbps)", "Ping (ms)"])
            
            # Escreve os dados do teste atual
            escritor.writerow([data_atual, f"{down:.2f}", f"{up:.2f}", f"{ping:.0f}"])
    
    def abrir_historico(self):
        arquivo = "historico.csv"
        if os.path.exists(arquivo):
            # No Windows, isso abre o arquivo com o programa padrão
            os.startfile(arquivo)
        else:
            self.label_status.configure(text="Status: Histórico ainda não existe!")
    
    def animar_valor(self, label, valor_final, atual=0.0):
        # Velocidade da subida: quanto menor o divisor, mais rápido sobe
        passo = valor_final / 30 
        
        if atual < valor_final:
            novo_valor = atual + passo
            if novo_valor > valor_final: novo_valor = valor_final
            
            # Formatação visual: Mbps com 1 casa, Ping sem casas
            texto = f"{novo_valor:.1f}" if valor_final > 10 else f"{novo_valor:.0f}"
            label.configure(text=texto)
            
            # Chama a si mesma após 20ms para criar o efeito de movimento
            self.after(20, lambda: self.animar_valor(label, valor_final, novo_valor))

    def iniciar_thread_teste(self):
        # Muda o estado do botão e status
        self.btn_start.configure(state="disabled", text="TESTANDO...")
        self.label_status.configure(text="Status: Conectando ao servidor...")
        
        # Cria e inicia a thread
        thread = threading.Thread(target=self.executar_teste)
        thread.start()

    def executar_teste(self):
        try:
            # --- ZERAR VALORES ANTERIORES ---
            self.val_down.configure(text="0.0")
            self.val_up.configure(text="0.0")
            self.val_ping.configure(text="0")

            st = speedtest.Speedtest(secure=True)
            st.get_servers()
            st.get_best_server()
            
            self.label_status.configure(text="Status: Testando Download...")
            down_speed = st.download() / 1_000_000
            self.after(0, lambda: self.animar_valor(self.val_down, down_speed))

            self.label_status.configure(text="Status: Testando Upload...")
            up_speed = st.upload() / 1_000_000
            self.after(0, lambda: self.animar_valor(self.val_up, up_speed))

            ping = st.results.ping
            self.after(0, lambda: self.animar_valor(self.val_ping, ping))
            self.salvar_historico(down_speed, up_speed, ping)

            self.label_status.configure(text="Status: Teste Finalizado!")
        except Exception as e:
            print(f"Erro detalhado: {e}") 
            self.label_status.configure(text="Status: Erro de Conexão")
        finally:
            self.btn_start.configure(state="normal", text="START TEST")

if __name__ == "__main__":
    app = SpeedTestApp()
    app.mainloop()