import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class TesteMongo:

    def __init__(self):
        self.cliente = None
        self.db = None
        self.colecao = None

    def conectar(self):
        # uri = "mongodb://204.236.201.27:27017/"
        uri = "mongodb://professor:professor@204.236.201.27:27017/?authSource=admin"
        
        try:
            self.cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.cliente.admin.command("ping")

            self.db = self.cliente["universidade"]

            # Criando uma variável independente para cada coleção
            self.colecao_usuarios = self.db["usuarios"]
            self.colecao_cursos = self.db["cursos"]
            self.colecao_disciplinas = self.db["disciplinas"]
            self.colecao_projetos = self.db["projetos"]
            self.colecao_turmas = self.db["turmas"]

            print("Conectado ao banco e a todas as coleções!")
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            sys.exit(1)

    # ==========================================
    # 1. CREATE (Inserir)
    # ==========================================
    def inserir_usuario(self): # Inserir para cada coleção
        print("\n--- INSERIR NOVO USUÁRIO ---")
        
        # 1. Coleta de Dados Gerais (Comuns a todos)
        cpf = input("Digite o CPF (será o _id): ").strip()
        nome = input("Digite o Nome: ").strip()
        login = input("Digite o Login: ").strip()
        senha = input("Digite a Senha: ").strip()
        
        # Coleta de Emails (Tratando como lista)
        print("Digite os e-mails separados por vírgula (ou pressione Enter se não houver):")
        emails_input = input()
        lista_emails = [e.strip() for e in emails_input.split(",")] if emails_input else None

        # Coleta de Telefones (Tratando como lista)
        print("Digite os telefones separados por vírgula (ou pressione Enter se não houver):")
        telefones_input = input()
        lista_telefones = [t.strip() for t in telefones_input.split(",")] if telefones_input else None

        # 2. Criação do esqueleto do documento com os dados gerais
        novo_usuario = {
            "_id": cpf,
            "nome": nome,
            "login": login,
            "senha": senha,
            "data_nascimento": None, # Pode ser implementado depois com tratamento de data
            "email": lista_emails,
            "telefone": lista_telefones
        }

        # 3. Identificação do Tipo de Usuário (Subdocumento)
        print("\nQual o tipo do usuário?")
        print("1 - Professor")
        print("2 - Estudante")
        tipo = input("Escolha uma opção: ").strip()

        if tipo == "1":
            print("\n--- Dados do Professor ---")
            mat_prof = input("Matrícula do Professor: ").strip()
            depto = input("Departamento (ex: DCOMP): ").strip()
            formacao = input("Formação (ex: Doutorado): ").strip()
            salario = float(input("Salário (ex: 1500.00): ") or 0)

            # Monta o objeto interno do professor
            novo_usuario["professor"] = {
                "mat_professor": mat_prof,
                "departamento": depto,
                "formacao": formacao,
                "data_admissao": None,
                "tipo_jornada_trabalho": "40h",
                "salario": salario
            }
            
        elif tipo == "2":
            print("\n--- Dados do Estudante ---")
            mat_est = input("Matrícula do Estudante: ").strip()
            ano_ingresso = int(input("Ano de Ingresso: ") or 2026)
            mc = float(input("Média de Conclusão (MC): ") or 0.0)

            # Monta o objeto interno do estudante
            novo_usuario["estudante"] = {
                "mat_estudante": mat_est,
                "MC": mc,
                "ano_ingresso": ano_ingresso,
                "vinculos": [] # Pode iniciar vazio ou criar um vínculo padrão
            }
        else:
            print("Opção de tipo inválida! O usuário será inserido sem perfil específico.")

        # 4. Envia o documento estruturado para a coleção de usuários
        try:
            resultado = self.colecao_usuarios.insert_one(novo_usuario)
            print(f"\n[Sucesso] Usuário cadastrado! ID: {resultado.inserted_id}")
        except Exception as e:
            print(f"\n[Erro] Falha ao inserir usuário no banco: {e}")

    # ==========================================
    # 2. READ (Buscar)
    # ==========================================
    # def buscar_professor_por_nome(self, nome_busca):
    #     # Criamos um filtro em formato de dicionário
    #     filtro = {"nome": nome_busca}
    #     professores = self.colecao.find(filtro)

    #     # find() retorna um cursor, precisamos iterar sobre ele
    #     encontrou = False
    #     for prof in professores:
    #         encontrou = True
    #         print(
    #             f"CPF: {prof['_id']} | Nome: {prof['nome']} | Depto: {prof['departamento']}"
    #         )

    #     if not encontrou:
    #         print("Nenhum professor encontrado com esse nome.")
    def buscar_usuario_por_cpf(self, cpf_busca):
        # Passamos o CPF como string diretamente, sem encapsular em ObjectId
        # filtro = {"_id": str(cpf_busca)}
        # usuario = self.colecao_usuarios.find_one(filtro)
        usuario = self.colecao_usuarios.find_one({"_id": str(cpf_busca)})

        if usuario:
            print(f"\n--- Usuário Encontrado ---")
            print(f"CPF/ID: {usuario.get('_id')}")
            print(f"Nome: {usuario.get('nome')}")
            print(f"Login: {usuario.get('login')}")

            # Tratamento seguro para campos que podem ser nulos (null)
            emails = usuario.get("email")
            if emails:
                print(f"Emails: {', '.join(emails)}")
            else:
                print("Emails: Nenhum cadastrado")

            telefones = usuario.get("telefone")
            if telefones:
                print(f"Telefones: {', '.join(telefones)}")
            else:
                print("Telefones: Nenhum cadastrado")

            # Verifica se o usuário é um Professor ou Estudante (Subdocumentos)
            if "professor" in usuario and usuario["professor"]:
                prof = usuario["professor"]
                print(f"Tipo: Professor (Matrícula: {prof.get('mat_professor')} | Depto: {prof.get('departamento')})")
            elif "estudante" in usuario and usuario["estudante"]:
                est = usuario["estudante"]
                print(f"Tipo: Estudante (Matrícula: {est.get('mat_estudante')} | Ano Ingresso: {est.get('ano_ingresso')})")

        else:
            print("Nenhum usuário encontrado com esse CPF.")

    # ==========================================
    # 3. UPDATE (Atualizar)
    # ==========================================
    def atualizar_departamento_professor(self, cpf, novo_departamento):
        filtro = {"_id": cpf}
        # O operador $set é obrigatório no Mongo para alterar campos específicos sem apagar o resto do documento
        novos_dados = {"$set": {"departamento": novo_departamento}}

        resultado = self.colecao.update_one(filtro, novos_dados)

        if resultado.matched_count > 0:
            print(f"Professor atualizado! Documentos modificados: {resultado.modified_count}")
        else:
            print("Nenhum professor encontrado com esse CPF.")

    # ==========================================
    # 4. DELETE (Apagar)
    # ==========================================
    def deletar_usuario(self):
        print("\n--- DELETAR USUÁRIO ---")
        cpf_deletar = input("Digite o CPF do usuário que deseja deletar: ").strip()

        if not cpf_deletar:
            print("[Aviso] CPF não pode ser vazio. Operação cancelada.")
            return

        # Antes de deletar, busca o usuário para mostrar quem será deletado, como em estrutura de dados para lidar com nós 
        usuario = self.colecao_usuarios.find_one({"_id": cpf_deletar})

        if usuario:
            print(f"\nUsuário encontrado: {usuario.get('nome')}")
            confirmacao = input(f"Tem certeza que deseja deletar permanentemente este usuário? (S/N): ").strip().upper()

            if confirmacao == "S":
                # O delete_one remove o documento inteiro correspondente ao filtro
                resultado = self.colecao_usuarios.delete_one({"_id": cpf_deletar})
                
                if resultado.deleted_count > 0:
                    print("[Sucesso] Usuário deletado do sistema.")
                else:
                    print("[Erro] Não foi possível deletar o usuário.")
            else:
                print("Operação de exclusão cancelada pelo usuário.")
                
        else:
            print("[Aviso] Nenhum usuário encontrado com esse CPF.")


# ==========================================
# Menu Interativo (Equivalente ao do-while)
# ==========================================
if __name__ == "__main__":
    teste = TesteMongo()
    teste.conectar()

    while True:
        print("\n========= MENU CRUD MONGO PROFESSOR =========")
        print("1 - Inserir usuário (Create)")
        print("2 - Buscar usuário por Nome (Read)")
        print("3 - Atualizar Departamento (Update)")
        print("4 - Deletar usuário (Delete)")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

        # O 'match/case' funciona exatamente como o switch-case (Disponível a partir do Python 3.10)
        match opcao:
            case "1":
                # cpf = input("Digite o CPF (será a Chave Primária): ")
                # nome = input("Digite o Nome: ")
                # depto = input("Digite o Departamento: ")
                # teste.inserir_professor(cpf, nome, depto)
                teste.inserir_usuario()                

            case "2":
                cpf_busca = input("Digite o CPF do usuário para buscar: ").strip()
                teste.buscar_usuario_por_cpf(cpf_busca)

            case "3":
                cpf = input("Digite o CPF do usuário a ser atualizado: ")
                depto = input("Digite o Novo Departamento: ")
                teste.atualizar_departamento_professor(cpf, depto)

            case "4":
                deletar_usuario()

            case "0":
                print("Encerrando o programa...")
                teste.fechar_conexao()
                break  # Sai do loop while

            case _:
                print("Opção inválida! Tente novamente.")
