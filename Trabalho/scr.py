#fazer a substituição dos IP de host e a porta de acordo com a atividade


import socket
import threading
import time

clientes_conectados = 0
mensagens_processadas = 0
tempo_inicio_servidor = time.time()

def lidar_com_cliente_tcp(socket_cliente):
    """Função para lidar com as mensagens do cliente TCP e realizar as operações solicitadas."""
    global mensagens_processadas, clientes_conectados
    try:
        while True:
            mensagem = socket_cliente.recv(1024).decode('utf-8')
            if not mensagem:
                print("Cliente desconectado.")
                break

            mensagens_processadas += 1
            print(f"Mensagem recebida: {mensagem}")

            if mensagem.startswith("invert "):
                texto_para_inverter = mensagem[7:]
                resposta = texto_para_inverter[::-1]
            elif mensagem.startswith("count "):
                texto_para_contar = mensagem[6:]
                resposta = str(len(texto_para_contar))
            elif mensagem.replace(" ", "").isdigit():
                try:
                    numeros = list(map(int, mensagem.split()))
                    resposta = str(sum(numeros))
                except ValueError:
                    resposta = "Erro: A mensagem contém elementos que não são números."
            else:
                resposta = "Comando inválido. Use 'invert <texto>', 'count <texto>' ou 'números separados por espaço'."

            print(f"Resposta enviada: {resposta}")
            socket_cliente.send(resposta.encode('utf-8'))
    except Exception as e:
        print(f"Erro na conexão com o cliente: {e}")
    finally:
        clientes_conectados -= 1
        socket_cliente.close()

def iniciar_servidor_tcp(host='127.0.0.1', porta=65432):
    global clientes_conectados
    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_servidor.bind((host, porta))
    socket_servidor.listen(5)
    print(f"Servidor TCP iniciado em {host}:{porta}")

    try:
        while True:
            socket_cliente, endereco_cliente = socket_servidor.accept()
            clientes_conectados += 1
            print(f"Cliente TCP conectado: {endereco_cliente}")
            thread_cliente = threading.Thread(target=lidar_com_cliente_tcp, args=(socket_cliente,))
            thread_cliente.start()
    except KeyboardInterrupt:
        print("Servidor finalizado pelo usuário.")
    except Exception as e:
        print(f"Erro no servidor: {e}")
    finally:
        socket_servidor.close()

def lidar_com_cliente_udp(socket_servidor):
    """Função para lidar com mensagens de clientes UDP."""
    global mensagens_processadas
    try:
        while True:
            mensagem, endereco_cliente = socket_servidor.recvfrom(1024)
            mensagem = mensagem.decode('utf-8')
            mensagens_processadas += 1
            print(f"Mensagem UDP recebida de {endereco_cliente}: {mensagem}")

            if mensagem.startswith("UPPER:"):
                resposta = mensagem[6:].upper()
            elif mensagem.startswith("REVERSE:"):
                resposta = mensagem[8:][::-1]
            elif mensagem.startswith("CALC:"):
                try:
                    resposta = str(eval(mensagem[5:]))
                except Exception as e:
                    resposta = f"Erro ao calcular: {e}"
            elif mensagem == "PING":
                resposta = "PONG"
            elif mensagem == "TIME":
                resposta = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            else:
                resposta = "Comando inválido."

            socket_servidor.sendto(resposta.encode('utf-8'), endereco_cliente)
            print(f"Resposta enviada para {endereco_cliente}: {resposta}")
    except Exception as e:
        print(f"Erro na conexão com o cliente UDP: {e}")

def iniciar_servidor_udp(host='127.0.0.1', porta=65433):
    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_servidor.bind((host, porta))
    print(f"Servidor UDP iniciado em {host}:{porta}")

    try:
        lidar_com_cliente_udp(socket_servidor)
    except KeyboardInterrupt:
        print("Servidor UDP finalizado pelo usuário.")
    except Exception as e:
        print(f"Erro no servidor UDP: {e}")
    finally:
        socket_servidor.close()

def imprimir_estatisticas_servidor():
    tempo_atividade = time.time() - tempo_inicio_servidor
    print("\n=== Estatísticas do Servidor ===")
    print(f"Clientes TCP conectados atualmente: {clientes_conectados}")
    print(f"Total de mensagens processadas: {mensagens_processadas}")
    print(f"Tempo de atividade do servidor: {tempo_atividade:.2f} segundos")

if __name__ == "__main__":
    thread_estatisticas = threading.Thread(target=imprimir_estatisticas_servidor)
    thread_estatisticas.daemon = True
    thread_estatisticas.start()

    thread_tcp = threading.Thread(target=iniciar_servidor_tcp)
    thread_tcp.start()

    thread_udp = threading.Thread(target=iniciar_servidor_udp)
    thread_udp.start()