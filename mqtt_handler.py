import paho.mqtt.client as mqtt

class MqttElevadorClient:
    def __init__(self, on_chamada_callback):
        self.client = mqtt.Client()
        self.on_chamada_callback = on_chamada_callback
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def conectar(self, broker="localhost", porta=1883):
        self.client.connect(broker, porta, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("✅ Conectado ao broker MQTT")
        self.client.subscribe("elevador/chamar")

    def on_message(self, client, userdata, msg):
        try:
            destino = int(msg.payload.decode())
            print(f"📡 Andar chamado via MQTT: {destino} m")
            self.on_chamada_callback(destino)
        except:
            print("❌ Erro: mensagem MQTT inválida.")
