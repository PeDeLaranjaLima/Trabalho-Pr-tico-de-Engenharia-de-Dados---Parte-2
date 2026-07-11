import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class TesteMongo:

    def __init__(self):
        self.cliente = None
        self.db = None

    def conectar(self):
        uri = "mongodb://professor:professor@54.242.65.141:27017/?authSource=admin"
        
        try:
            self.cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.cliente.admin.command("ping")

            self.db = self.cliente["universidade"]

            # Coleções
            self.colecao_usuarios = self.db["usuarios"]
            self.colecao_cursos = self.db["cursos"]
            self.colecao_disciplinas = self.db["disciplinas"]
            self.colecao_projetos = self.db["projetos"]
            self.colecao_turmas = self.db["turmas"]

            print("Conectado ao banco e a todas as coleções!")
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            sys.exit(1)

    def fechar_conexao(self):
        if self.cliente:
            self.cliente.close()
            print("Conexão com o MongoDB fechada.")

    # ==========================================
    # CRUD USUÁRIOS (Seu código original corrigido)
    # ==========================================
    def inserir_usuario(self):
        print("\n--- INSERIR NOVO USUÁRIO ---")
        cpf = input("Digite o CPF (será o _id): ").strip()
        nome = input("Digite o Nome: ").strip()
        login = input("Digite o Login: ").strip()
        senha = input("Digite a Senha: ").strip()
        
        print("Digite os e-mails separados por vírgula (ou pressione Enter se não houver):")
        emails_input = input()
        lista_emails = [e.strip() for e in emails_input.split(",")] if emails_input else None

        print("Digite os telefones separados por vírgula (ou pressione Enter se não houver):")
        telefones_input = input()
        lista_telefones = [t.strip() for t in telefones_input.split(",")] if telefones_input else None

        novo_usuario = {
            "_id": cpf, "nome": nome, "login": login, "senha": senha,
            "data_nascimento": None, "email": lista_emails, "telefone": lista_telefones
        }

        print("\nQual o tipo do usuário? (1 - Professor | 2 - Estudante)")
        tipo = input("Escolha uma opção: ").strip()

        if tipo == "1":
            mat_prof = input("Matrícula do Professor: ").strip()
            depto = input("Departamento (ex: DCOMP): ").strip()
            formacao = input("Formação (ex: Doutorado): ").strip()
            salario = float(input("Salário (ex: 1500.00): ") or 0)
            novo_usuario["professor"] = {
                "mat_professor": mat_prof, "departamento": depto, "formacao": formacao,
                "data_admissao": None, "tipo_jornada_trabalho": "40h", "salario": salario
            }
        elif tipo == "2":
            mat_est = input("Matrícula do Estudante: ").strip()
            ano_ingresso = int(input("Ano de Ingresso: ") or 2026)
            mc = float(input("Média de Conclusão (MC): ") or 0.0)
            novo_usuario["estudante"] = {
                "mat_estudante": mat_est, "MC": mc, "ano_ingresso": ano_ingresso, "vinculos": []
            }

        try:
            self.colecao_usuarios.insert_one(novo_usuario)
            print(f"\n[Sucesso] Usuário cadastrado! ID: {cpf}")
        except Exception as e:
            print(f"\n[Erro] Falha ao inserir: {e}")

    def buscar_usuario_por_cpf(self, cpf_busca):
        usuario = self.colecao_usuarios.find_one({"_id": str(cpf_busca)})
        if usuario:
            print(f"\n--- Usuário Encontrado ---")
            print(f"CPF: {usuario.get('_id')} | Nome: {usuario.get('nome')} | Login: {usuario.get('login')}")
            print(f"Emails: {', '.join(usuario.get('email') or ['Nenhum'])}")
            print(f"Telefones: {', '.join(usuario.get('telefone') or ['Nenhum'])}")
            if "professor" in usuario: print(f"Perfil: Professor | Depto: {usuario['professor'].get('departamento')}")
            elif "estudante" in usuario: print(f"Perfil: Estudante | Matrícula: {usuario['estudante'].get('mat_estudante')}")
        else:
            print("Nenhum usuário encontrado com esse CPF.")

    def atualizar_departamento_professor(self, cpf, novo_departamento):
        resultado = self.colecao_usuarios.update_one({"_id": cpf}, {"$set": {"professor.departamento": novo_departamento}})
        print(f"Documentos modificados: {resultado.modified_count}" if resultado.matched_count > 0 else "Nenhum professor encontrado.")

    def deletar_usuario(self):
        print("\n--- DELETAR USUÁRIO ---")
        cpf = input("Digite o CPF do usuário: ").strip()
        if not cpf: return
        usuario = self.colecao_usuarios.find_one({"_id": cpf})
        if usuario:
            if input(f"Deletar {usuario.get('nome')}? (S/N): ").strip().upper() == "S":
                self.colecao_usuarios.delete_one({"_id": cpf})
                print("[Sucesso] Deletado.")
        else:
            print("[Aviso] Nenhum usuário encontrado.")

    # ==========================================
    # CRUD CURSOS
    # ==========================================
    def inserir_curso(self):
        print("\n--- INSERIR CURSO ---")
        id_curso = input("ID do Curso (ex: CCO): ").strip()
        nome = input("Nome do Curso: ").strip()
        ch = int(input("Carga Horária Total (horas): ") or 0)
        periodos = int(input("Número de Períodos: ") or 0)
        try:
            self.colecao_cursos.insert_one({"_id": id_curso, "nome": nome, "carga_horaria": ch, "periodos": periodos})
            print(f"[Sucesso] Curso {id_curso} inserido!")
        except Exception as e: print(f"[Erro] {e}")

    def buscar_curso(self):
        id_curso = input("Digite o ID do Curso para buscar: ").strip()
        curso = self.colecao_cursos.find_one({"_id": id_curso})
        if curso:
            print(f"ID: {curso['_id']} | Nome: {curso['nome']} | CH: {curso.get('carga_horaria')} | Períodos: {curso.get('periodos')}")
        else: print("Curso não encontrado.")

    def atualizar_curso(self):
        id_curso = input("Digite o ID do Curso a atualizar: ").strip()
        novo_nome = input("Novo nome (deixe vazio para manter o atual): ").strip()
        novos_dados = {"$set": {"nome": novo_nome}} if novo_nome else {"$set": {}}
        if not novo_nome: print("Nenhum dado fornecido para atualizar."); return
        resultado = self.colecao_cursos.update_one({"_id": id_curso}, novos_dados)
        print("Atualizado com sucesso!" if resultado.modified_count > 0 else "Nada foi alterado.")

    def deletar_curso(self):
        id_curso = input("Digite o ID do Curso a deletar: ").strip()
        resultado = self.colecao_cursos.delete_one({"_id": id_curso})
        print("[Sucesso] Curso deletado." if resultado.deleted_count > 0 else "Curso não encontrado.")

    # ==========================================
    # CRUD DISCIPLINAS
    # ==========================================
    def inserir_disciplina(self):
        print("\n--- INSERIR DISCIPLINA ---")
        id_disc = input("ID da Disciplina (ex: DCOMP001): ").strip()
        nome = input("Nome da Disciplina: ").strip()
        ch = int(input("Carga Horária (horas): ") or 0)
        curso_vinculo = input("ID do Curso ao qual pertence (ex: CCO): ").strip()
        try:
            self.colecao_disciplinas.insert_one({"_id": id_disc, "nome": nome, "carga_horaria": ch, "id_curso": curso_vinculo})
            print(f"[Sucesso] Disciplina {id_disc} inserida!")
        except Exception as e: print(f"[Erro] {e}")

    def buscar_disciplina(self):
        id_disc = input("Digite o ID da Disciplina: ").strip()
        disc = self.colecao_disciplinas.find_one({"_id": id_disc})
        if disc:
            print(f"ID: {disc['_id']} | Nome: {disc['nome']} | CH: {disc.get('carga_horaria')} | Curso: {disc.get('id_curso')}")
        else: print("Disciplina não encontrada.")

    def atualizar_disciplina(self):
        id_disc = input("Digite o ID da Disciplina a atualizar: ").strip()
        nova_ch = input("Nova Carga Horária (apenas número, vazio para cancelar): ").strip()
        if nova_ch:
            self.colecao_disciplinas.update_one({"_id": id_disc}, {"$set": {"carga_horaria": int(nova_ch)}})
            print("Atualizado com sucesso!")
        else: print("Operação cancelada.")

    def deletar_disciplina(self):
        id_disc = input("Digite o ID da Disciplina a deletar: ").strip()
        resultado = self.colecao_disciplinas.delete_one({"_id": id_disc})
        print("[Sucesso] Disciplina deletada." if resultado.deleted_count > 0 else "Disciplina não encontrada.")

    # ==========================================
    # CRUD PROJETOS
    # ==========================================
    def inserir_projeto(self):
        print("\n--- INSERIR PROJETO ---")
        id_proj = input("ID do Projeto (ex: PROJ2024_01): ").strip()
        titulo = input("Título do Projeto: ").strip()
        descricao = input("Descrição resumida: ").strip()
        cpf_prof = input("CPF do Professor responsável: ").strip()
        status = input("Status (ex: Em andamento, Concluído): ").strip() or "Em andamento"
        try:
            self.colecao_projetos.insert_one({"_id": id_proj, "titulo": titulo, "descricao": descricao, "cpf_professor": cpf_prof, "status": status})
            print(f"[Sucesso] Projeto {id_proj} inserido!")
        except Exception as e: print(f"[Erro] {e}")

    def buscar_projeto(self):
        id_proj = input("Digite o ID do Projeto: ").strip()
        proj = self.colecao_projetos.find_one({"_id": id_proj})
        if proj:
            print(f"ID: {proj['_id']} | Título: {proj['titulo']} | Professor: {proj.get('cpf_professor')} | Status: {proj.get('status')}")
        else: print("Projeto não encontrado.")

    def atualizar_projeto(self):
        id_proj = input("Digite o ID do Projeto a atualizar: ").strip()
        novo_status = input("Novo Status: ").strip()
        resultado = self.colecao_projetos.update_one({"_id": id_proj}, {"$set": {"status": novo_status}})
        print("Atualizado com sucesso!" if resultado.modified_count > 0 else "Nada foi alterado.")

    def deletar_projeto(self):
        id_proj = input("Digite o ID do Projeto a deletar: ").strip()
        resultado = self.colecao_projetos.delete_one({"_id": id_proj})
        print("[Sucesso] Projeto deletado." if resultado.deleted_count > 0 else "Projeto não encontrado.")

    # ==========================================
    # CRUD TURMAS
    # ==========================================
    def inserir_turma(self):
        print("\n--- INSERIR TURMA ---")
        id_turma = input("ID da Turma (ex: DCOMP001-2024-1): ").strip()
        id_disc = input("ID da Disciplina: ").strip()
        cpf_prof = input("CPF do Professor que ministra: ").strip()
        ano = int(input("Ano (ex: 2024): ") or 2024)
        semestre = int(input("Semestre (1 ou 2): ") or 1)
        try:
            self.colecao_turmas.insert_one({"_id": id_turma, "id_disciplina": id_disc, "cpf_professor": cpf_prof, "ano": ano, "semestre": semestre})
            print(f"[Sucesso] Turma {id_turma} inserida!")
        except Exception as e: print(f"[Erro] {e}")

    def buscar_turma(self):
        id_turma = input("Digite o ID da Turma: ").strip()
        turma = self.colecao_turmas.find_one({"_id": id_turma})
        if turma:
            print(f"ID: {turma['_id']} | Disciplina: {turma.get('id_disciplina')} | Professor: {turma.get('cpf_professor')} | Período: {turma.get('ano')}/{turma.get('semestre')}")
        else: print("Turma não encontrada.")

    def atualizar_turma(self):
        id_turma = input("Digite o ID da Turma a atualizar: ").strip()
        novo_prof = input("Novo CPF do Professor: ").strip()
        resultado = self.colecao_turmas.update_one({"_id": id_turma}, {"$set": {"cpf_professor": novo_prof}})
        print("Professor da turma atualizado!" if resultado.modified_count > 0 else "Nada foi alterado.")

    def deletar_turma(self):
        id_turma = input("Digite o ID da Turma a deletar: ").strip()
        resultado = self.colecao_turmas.delete_one({"_id": id_turma})
        print("[Sucesso] Turma deletada." if resultado.deleted_count > 0 else "Turma não encontrada.")


# ==========================================
# Funções de Sub-Menu (Para não poluir o main)
# ==========================================
def submenu_cursos(teste):
    while True:
        print("\n--- GERENCIAR CURSOS ---")
        print("1- Inserir | 2- Buscar | 3- Atualizar | 4- Deletar | 0- Voltar")
        op = input("Escolha: ")
        match op: # O 'match/case' funciona exatamente como o switch-case
            case "1": teste.inserir_curso()
            case "2": teste.buscar_curso()
            case "3": teste.atualizar_curso()
            case "4": teste.deletar_curso()
            case "0": break
            case _: print("Opção inválida.")

def submenu_disciplinas(teste):
    while True:
        print("\n--- GERENCIAR DISCIPLINAS ---")
        print("1- Inserir | 2- Buscar | 3- Atualizar | 4- Deletar | 0- Voltar")
        op = input("Escolha: ")
        match op:
            case "1": teste.inserir_disciplina()
            case "2": teste.buscar_disciplina()
            case "3": teste.atualizar_disciplina()
            case "4": teste.deletar_disciplina()
            case "0": break
            case _: print("Opção inválida.")

def submenu_projetos(teste):
    while True:
        print("\n--- GERENCIAR PROJETOS ---")
        print("1- Inserir | 2- Buscar | 3- Atualizar | 4- Deletar | 0- Voltar")
        op = input("Escolha: ")
        match op:
            case "1": teste.inserir_projeto()
            case "2": teste.buscar_projeto()
            case "3": teste.atualizar_projeto()
            case "4": teste.deletar_projeto()
            case "0": break
            case _: print("Opção inválida.")

def submenu_turmas(teste):
    while True:
        print("\n--- GERENCIAR TURMAS ---")
        print("1- Inserir | 2- Buscar | 3- Atualizar | 4- Deletar | 0- Voltar")
        op = input("Escolha: ")
        match op:
            case "1": teste.inserir_turma()
            case "2": teste.buscar_turma()
            case "3": teste.atualizar_turma()
            case "4": teste.deletar_turma()
            case "0": break
            case _: print("Opção inválida.")

def submenu_usuarios(teste):
    while True:
        print("\n--- GERENCIAR USUÁRIOS ---")
        print("1- Inserir | 2- Buscar por CPF | 3- Atualizar Depto Professor | 4- Deletar | 0- Voltar")
        op = input("Escolha: ")
        match op:
            case "1": teste.inserir_usuario()
            case "2": 
                cpf = input("Digite o CPF: ").strip()
                teste.buscar_usuario_por_cpf(cpf)
            case "3":
                cpf = input("Digite o CPF do Professor: ").strip()
                depto = input("Digite o Novo Departamento: ").strip()
                teste.atualizar_departamento_professor(cpf, depto)
            case "4": teste.deletar_usuario()
            case "0": break
            case _: print("Opção inválida.")


# ==========================================
# Menu Principal
# ==========================================
if __name__ == "__main__":
    teste = TesteMongo()
    teste.conectar()

    while True:
        print("\n========= SISTEMA UNIVERSIDADE =========")
        print("1 - Usuários (Professores/Estudantes)")
        print("2 - Cursos")
        print("3 - Disciplinas")
        print("4 - Projetos")
        print("5 - Turmas")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

        match opcao:
            case "1": submenu_usuarios(teste)
            case "2": submenu_cursos(teste)
            case "3": submenu_disciplinas(teste)
            case "4": submenu_projetos(teste)
            case "5": submenu_turmas(teste)
            case "0":
                print("Encerrando o programa...")
                teste.fechar_conexao()
                break
            case _:
                print("Opção inválida! Tente novamente.")
