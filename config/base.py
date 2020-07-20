#Import's necessários (List import).
from discord.ext import commands
from database import Database
from os import listdir
# - Class da harumi com seus eventos.
class Harumi(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
         - Funções:
          self.load : Evitar de recarregar os modulos caso haja alguma queda.
          self.env : Obter informações 'dict' da classe da parte 'env' como token, links, etc.
          self.db : Fornecer os dados para a conexão da database do bot como url, name, a variável do bot.
        """
        self.loaded = False
        self.env = kwargs['env']
        self.db = Database(url=self.env.config.database.url, name=self.env.config.database.name, harumi=self)
    
    # - Evento para carregar o(s) plugin(s).
    async def on_start(self):
        # - Puxar todo os plugins de um directorio.
        plugins = [p[:-3] for p in listdir("plugins") if p.endswith(".py")]
        # - Contar quantos plugins existem.
        total_plugins = len(plugins)
        # - Enumerar todo os plugins e passar eles por um 'for', e após passar usar o 'try' para executar uma leitura do mesmo.
        for i, plugin in enumerate(plugins, 1):
          try:
             # - Carregar o plugin.
             self.load_extension(f"plugins.{plugin}")
          except Exception as e:
              # - Caso houver um erro ao carregar o plugin.
              print(f"[Plugin] : Erro ao carregar o plugin {plugin}.\n{e.__class__.__name__}: {e}")
          else:
            # - Quando o plugin carrega com sucesso.
            print(f"[Plugin] : O plugin {plugin} carregado com sucesso. ({i}/{total_plugins})")
        # - Após carregar o(s) plugin(s) deixar a condição do loaded 'true'.
        self.loaded = True


    # - Evento referente ao 'start'.
    async def on_ready(self):
       # - Executar o evento on_start caso loaded esteja 'false'.
       if not self.loaded:
          await self.on_start()
          print(f"[Session] : O bot {self.user.name} está online.")  

    # - Evento referente a bloqueios de usuários, canais, checks entre outros.
    async def on_message(self, message):
       # - Checar se a mensagem não originou de um 'dm' ou se o modulo estar carregado.
       if not self.loaded or message.guild is None:return   
       # - Checar se a mensagem não se originou de um bot ou checar se pode enviar comandos no canal.
       if message.author.bot or not message.channel.permissions_for(message.guild.me).send_messages:return
       # - Puxar as informações da mensagem como comandos, valores, canais, servidor etc.
       ctx = await self.get_context(message)
       # - Checar se o comando é valído, se o comando não estar em uma classe proibida, se o author é um admin.
       if not ctx.valid or ctx.command.cog_name in self.env.config.ignore and not ctx.author.id in self.env.staff:return
       # - Importar as informações do database pro context.
       ctx.db = await self.db.get_guild(ctx.guild.id)
       try:
          # - Invocar o comando pelo contexto e poder manipular alguns eventos.
          await self.invoke(ctx)
       except Exception as e:
            # - Invocar o evento command_error caso ouver algum erro na execução do comando.
            self.dispatch('command_error', ctx, e)         