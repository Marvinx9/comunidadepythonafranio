# from sqlalchemy import create_engine
# import pymysql
#
# engine = create_engine("mysql+pymysql://user:pw@host/db", pool_pre_ping=True)

# from comunidadeimpressionadora import app, database
# # #
# with app.app_context():
#     database.drop_all()
#     database.create_all()

# with app.app_context():
#     usuario = Usuario(username="Lira", email="lira@gmail.com", senha="123456")
#     usuario2 = Usuario(username="João", email="joao@gmail.com", senha="123456")
#
#     database.session.add(usuario)
#     database.session.add(usuario2)
#
#     database.session.commit()

# # printando todos os meus usuários
# with app.app_context():
#     meus_usuarios = Usuario.query.all()
#     print(meus_usuarios)
#
# # printando os meus usuários por meio de um filtro
# with app.app_context():
#     usuario_teste = Usuario.query.filter_by(email='lira@gmail.com').first()
#     print(usuario_teste.username)

# with app.app_context():
#     meu_post = Post(id_usuario=1, titulo="Primeiro post do Lira", corpo="Lira voando")
#     database.session.add(meu_post)
#     database.session.commit()


# with app.app_context():
#     post = Post.query.first()
#     print(post.titulo)
#     print(post.autor.email)

# # criando novamente o banco de dados
# with app.app_context():
#     database.drop_all()
#     database.create_all()

# from comunidadeimpressionadora.models import Usuario
# from comunidadeimpressionadora import app
# with app.app_context():
#     usuario = Usuario.query.first()
#     print(usuario.senha)
from comunidadeimpressionadora import app, database
from comunidadeimpressionadora.models import Usuario
with app.app_context():
    usuario = Usuario.query.filter_by(email='afraniotest@gmail.com').first()
    print(usuario.cursos)