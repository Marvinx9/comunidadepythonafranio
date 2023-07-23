from flask import render_template, redirect, url_for, flash, request, abort
from comunidadeimpressionadora import app, database, bcrypt
from comunidadeimpressionadora.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost
from comunidadeimpressionadora.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image


@app.route('/')
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)

@app.route('/contato')
def contato():
    return render_template('contato.html')

@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()
    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login feito com sucesso no e-mail: {form_login.email.data}', 'alert-success')
            par_next = request.args.get('next')
            redirects_seguros = ['/', '/contatos', '/clientes', '/perfil', '/login', '/post/criar', '/usuarios']
            if par_next in redirects_seguros:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'E-mail ou Senha Incorretos', 'alert-danger')

    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data).decode("utf-8")
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()

        flash(f'Conta criada para o e-mail: {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash(f'Logout feito com Sucesso', 'alert-success')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)


@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit(): #caso o usuario preencheu corretamente o form
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post Criado com Sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)


def salvar_imagem(imagem):
    codigo = secrets.token_hex(8) # adicionar um código aleatório no mome da imagem
    nome, extensao = os.path.splitext(imagem.filename) #separando o nome da imagem da extensão
    nome_arquivo = nome + codigo + extensao #juntar os 3 nomes
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (400, 400)# reduzir o tamanho da imagem
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo) # salvar a imagem na pasta fotos_perfil
    # mudar o campo foto_perfil do usuário para o novo nome da imagem
    return nome_arquivo

def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name:
            # verifica se o campo foi marcado
            if campo.data:
                #adicionar o texto do campo.label (Excel Impressionador) na lista de cursos
                lista_cursos.append(campo.label.text)
    return ';'.join(lista_cursos)

@app.route('/perfil/editar', methods=['GET' ,'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    # o método (validate_on_submit) verifica automaticamente se todas as funções (validade_) do arquivo 'forms.py' estão válidos
    if form.validate_on_submit():
        # os dados salvos do usuário passa a ser os novos dados que ele preencheu
        current_user.email = form.email.data
        current_user.username = form.username.data
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        current_user.cursos = atualizar_cursos(form)


        database.session.commit()
        # Exibir mensagem de confirmação
        flash(f'Perfil atualizado com Sucesso', 'alert-success')
        # retorna o usuário para a página de perfil
        return redirect(url_for('perfil'))
    # ocorre caso o usuário somente clique em editar perfil, mas não clique em postar uma atualização mo perfil
    # serve para aparecer o nome e e-mail default no local de preenchimento
    elif request.method == "GET":
        form.email.data = current_user.email
        form.username.data = current_user.username
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form=form)

@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == 'GET':  #aparece o titulo e corpo para o usuario editar
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():  #edição do posta do usuario
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post Editado com Sucesso', 'alert-success')
            return redirect(url_for('home'))
            #logica de editar post
    else:
        form = None
    return render_template('post.html', post=post, form=form)

@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Postagem Excluída com Sucesso', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)
