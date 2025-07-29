	#!/usr/bin/env python3
	"""
	🚀 GitHub Repository Creator & Uploader
	Creează un repository nou pe GitHub și uploadează toate fișierele din Manufacturing project
	"""

	import os
	import subprocess
	import requests
	import json
	import shutil
	from pathlib import Path
	import time
	from datetime import datetime

	class GitHubUploader:
		def __init__(self):
			# CONFIGURARE - COMPLETATĂ CU DATELE TALE
			self.github_username = "me-suzy"  # ✅ Username-ul tău GitHub
			self.github_token = "YOUR-TOKEN"  # ✅ Token-ul tău GitHub
			self.repo_name = "Manufacturing-Production-Scheduler"
			self.repo_description = "🏭 Advanced Manufacturing Production Scheduler with AI Optimization"
			
			# Calea sursă cu Manufacturing files
			self.source_path = r"e:\Carte\BB\17 - Site Leadership\alte\Ionel Balauta\Aryeht\Task 1 - Traduce tot site-ul\Doar Google Web\Andreea\Meditatii\2023\Manufacturing"
			
			# Calea temporară pentru repository
			self.temp_repo_path = f"temp_{self.repo_name}"
			
			print("🚀 GitHub Uploader initialized")
			print(f"📁 Source: {self.source_path}")
			print(f"📦 Repo: {self.repo_name}")

		def check_prerequisites(self):
			"""Verifică că Git și credentialele sunt configurate"""
			try:
				# Verifică Git
				result = subprocess.run(["git", "--version"], capture_output=True, text=True)
				if result.returncode != 0:
					raise Exception("Git is not installed or not in PATH")
				print(f"✅ Git found: {result.stdout.strip()}")
				
				# Verifică directory source
				if not os.path.exists(self.source_path):
					raise Exception(f"Source directory not found: {self.source_path}")
				print(f"✅ Source directory found: {len(os.listdir(self.source_path))} files")
				
				# Verifică credentiale
				if self.github_username == "YOUR_GITHUB_USERNAME":
					raise Exception("⚠️ Please update github_username in the script!")
				if self.github_token == "YOUR_GITHUB_TOKEN":
					raise Exception("⚠️ Please update github_token in the script!")
				
				print("✅ Prerequisites check passed")
				return True
				
			except Exception as e:
				print(f"❌ Prerequisites check failed: {e}")
				return False

		def create_github_repo(self):
			"""Creează repository pe GitHub folosind API"""
			try:
				print("\n📡 Creating GitHub repository...")
				
				url = "https://api.github.com/user/repos"
				headers = {
					"Authorization": f"token {self.github_token}",
					"Accept": "application/vnd.github.v3+json"
				}
				
				data = {
					"name": self.repo_name,
					"description": self.repo_description,
					"private": False,  # Schimbă la True pentru repo privat
					"auto_init": False,
					"gitignore_template": "Python",
					"license_template": "mit"
				}
				
				response = requests.post(url, headers=headers, json=data)
				
				if response.status_code == 201:
					repo_info = response.json()
					print(f"✅ Repository created successfully!")
					print(f"🔗 URL: {repo_info['html_url']}")
					print(f"📋 Clone URL: {repo_info['clone_url']}")
					return repo_info
				elif response.status_code == 422:
					print(f"⚠️ Repository {self.repo_name} already exists")
					# Încearcă să obții informațiile repo-ului existent
					get_url = f"https://api.github.com/repos/{self.github_username}/{self.repo_name}"
					get_response = requests.get(get_url, headers=headers)
					if get_response.status_code == 200:
						print("ℹ️ Using existing repository")
						return get_response.json()
					else:
						raise Exception("Cannot access existing repository")
				else:
					raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
					
			except Exception as e:
				print(f"❌ Failed to create GitHub repository: {e}")
				return None

		def prepare_local_repo(self, repo_info):
			"""Pregătește repository-ul local"""
			try:
				print(f"\n📁 Preparing local repository...")
				
				# Șterge directorul temporar dacă există
				if os.path.exists(self.temp_repo_path):
					shutil.rmtree(self.temp_repo_path)
					print(f"🗑️ Cleaned up existing temp directory")
				
				# Creează directorul nou
				os.makedirs(self.temp_repo_path)
				os.chdir(self.temp_repo_path)
				print(f"📂 Created temp directory: {os.getcwd()}")
				
				# Inițializează Git
				subprocess.run(["git", "init"], check=True)
				subprocess.run(["git", "branch", "-M", "main"], check=True)
				print("✅ Git repository initialized")
				
				# Copiază toate fișierele din Manufacturing
				print(f"📋 Copying files from {self.source_path}...")
				copied_files = 0
				
				for root, dirs, files in os.walk(self.source_path):
					# Calculează calea relativă
					rel_path = os.path.relpath(root, self.source_path)
					if rel_path == '.':
						dest_dir = '.'
					else:
						dest_dir = rel_path
						os.makedirs(dest_dir, exist_ok=True)
					
					# Copiază fișierele
					for file in files:
						# Skip fișiere temporare și cache
						if file.endswith(('.pyc', '.pyo', '.pyd', '__pycache__')):
							continue
						if file.startswith('.'):
							continue
							
						src_file = os.path.join(root, file)
						dest_file = os.path.join(dest_dir, file)
						
						try:
							shutil.copy2(src_file, dest_file)
							copied_files += 1
							print(f"   📄 {dest_file}")
						except Exception as e:
							print(f"   ⚠️ Failed to copy {file}: {e}")
				
				print(f"✅ Copied {copied_files} files")
				
				# Creează README.md
				self.create_readme()
				
				# Creează .gitignore
				self.create_gitignore()
				
				# Adaugă fișierele la Git
				subprocess.run(["git", "add", "."], check=True)
				print("✅ Files added to Git staging")
				
				return True
				
			except Exception as e:
				print(f"❌ Failed to prepare local repo: {e}")
				return False

		def create_readme(self):
			"""Creează README.md profesional"""
			readme_content = f"""# 🏭 Manufacturing Production Scheduler

	Advanced Manufacturing Production Scheduler with AI-powered optimization and real-time analytics.

	## 🚀 Features

	### 🏭 Production Management
	- **Production Lines**: Complete line management with capacity tracking
	- **Orders Management**: Advanced order handling with priorities and dependencies
	- **Timeline & Schedule**: Interactive Gantt-style timeline with drag & drop
	- **Real-time Analytics**: Live KPI monitoring and performance metrics

	### 🤖 AI Optimization
	- **Genetic Algorithm**: Advanced scheduling optimization
	- **Simulated Annealing**: Balance between speed and quality
	- **Greedy Algorithm**: Fast scheduling for urgent orders
	- **Continuous Optimization**: Background optimization engine

	### 📊 Analytics & Reporting
	- **KPI Dashboard**: Real-time efficiency, utilization, and delivery metrics
	- **Advanced Analytics**: Detailed production insights
	- **Custom Reports**: Exportable reports and analytics
	- **Performance Tracking**: Historical data and trends

	### 🎯 Interactive Interface
	- **Modern UI**: Dark theme with professional styling
	- **Drag & Drop**: Intuitive timeline interactions
	- **Real-time Updates**: Live metrics and status updates
	- **Responsive Design**: Optimized for different screen sizes

	## 🛠 Installation

	### Prerequisites
	- Python 3.8+
	- Required packages: `pandas`, `tkinter`, `openpyxl`

	### Setup
	```bash
	# Clone the repository
	git clone https://github.com/{self.github_username}/{self.repo_name}.git
	cd {self.repo_name}

	# Install dependencies
	pip install pandas openpyxl

	# Run the application
	python Manufacturing.py
	```

	## 📚 Usage

	### Starting the Application
	```bash
	python Manufacturing.py
	```

	### Main Features
	1. **Production Lines Tab**: Manage your production lines
	2. **Orders Management Tab**: Handle customer orders
	3. **Timeline & Schedule Tab**: Visual scheduling interface
	4. **Optimization & Analytics Tab**: AI-powered optimization

	### Quick Start
	1. Add your production lines in the "Production Lines" tab
	2. Create orders in the "Orders Management" tab
	3. Use the timeline to schedule orders visually
	4. Run optimization to improve efficiency

	## 🏗 Architecture

	### Core Components
	- `Manufacturing.py` - Main application and GUI
	- `gantt_view.py` - Interactive Gantt chart component
	- `orders_filter.py` - Advanced order filtering
	- `analytics_dashboard.py` - Analytics and reporting
	- `reports_generator.py` - Report generation system

	### Data Management
	- Excel-based data storage
	- Real-time data synchronization
	- Automatic backup system
	- JSON configuration management

	## 🎯 Key Metrics Tracked

	- **Overall Efficiency**: Production line performance
	- **On-Time Delivery**: Order completion rates
	- **Line Utilization**: Resource usage optimization
	- **Throughput**: Daily production capacity
	- **Critical Orders**: High priority order tracking

	## 🤝 Contributing

	1. Fork the repository
	2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
	3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
	4. Push to the branch (`git push origin feature/AmazingFeature`)
	5. Open a Pull Request

	## 📄 License

	This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

	## 👤 Author

	Created with ❤️ for modern manufacturing operations.

	## 🆕 Latest Updates

	- ✅ Interactive Timeline with Today highlighting
	- ✅ Advanced scroll support for all forms
	- ✅ Real-time metrics and KPI tracking
	- ✅ AI-powered scheduling optimization
	- ✅ Professional UI with dark theme

	## 📞 Support

	For support and questions, please open an issue in the GitHub repository.

	---

	**🏭 Built for the future of manufacturing** | Created on {datetime.now().strftime('%Y-%m-%d')}
	"""

			with open("README.md", "w", encoding="utf-8") as f:
				f.write(readme_content)
			print("✅ README.md created")

		def create_gitignore(self):
			"""Creează .gitignore pentru Python"""
			gitignore_content = """# Byte-compiled / optimized / DLL files
	__pycache__/
	*.py[cod]
	*$py.class

	# C extensions
	*.so

	# Distribution / packaging
	.Python
	build/
	develop-eggs/
	dist/
	downloads/
	eggs/
	.eggs/
	lib/
	lib64/
	parts/
	sdist/
	var/
	wheels/
	pip-wheel-metadata/
	share/python-wheels/
	*.egg-info/
	.installed.cfg
	*.egg
	MANIFEST

	# PyInstaller
	*.manifest
	*.spec

	# Installer logs
	pip-log.txt
	pip-delete-this-directory.txt

	# Unit test / coverage reports
	htmlcov/
	.tox/
	.nox/
	.coverage
	.coverage.*
	.cache
	nosetests.xml
	coverage.xml
	*.cover
	*.py,cover
	.hypothesis/
	.pytest_cache/

	# Translations
	*.mo
	*.pot

	# Django stuff:
	*.log
	local_settings.py
	db.sqlite3
	db.sqlite3-journal

	# Flask stuff:
	instance/
	.webassets-cache

	# Scrapy stuff:
	.scrapy

	# Sphinx documentation
	docs/_build/

	# PyBuilder
	target/

	# Jupyter Notebook
	.ipynb_checkpoints

	# IPython
	profile_default/
	ipython_config.py

	# pyenv
	.python-version

	# pipenv
	Pipfile.lock

	# PEP 582
	__pypackages__/

	# Celery stuff
	celerybeat-schedule
	celerybeat.pid

	# SageMath parsed files
	*.sage.py

	# Environments
	.env
	.venv
	env/
	venv/
	ENV/
	env.bak/
	venv.bak/

	# Spyder project settings
	.spyderproject
	.spyproject

	# Rope project settings
	.ropeproject

	# mkdocs documentation
	/site

	# mypy
	.mypy_cache/
	.dmypy.json
	dmypy.json

	# Pyre type checker
	.pyre/

	# Excel backup files
	*.xlsx.backup
	*.xls.backup

	# Manufacturing specific
	temp_*
	*.log
	backup_*
	test_*
	"""
			with open(".gitignore", "w", encoding="utf-8") as f:
				f.write(gitignore_content)
			print("✅ .gitignore created")

		def commit_and_push(self, repo_info):
			"""Face commit și push la GitHub"""
			try:
				print(f"\n📤 Committing and pushing to GitHub...")
				
				# Configurează Git user dacă nu e setat
				try:
					subprocess.run(["git", "config", "user.name", self.github_username], check=True)
					subprocess.run(["git", "config", "user.email", f"{self.github_username}@users.noreply.github.com"], check=True)
				except:
					print("⚠️ Git user config might already be set")
				
				# Commit
				commit_message = f"🏭 Initial commit: Manufacturing Production Scheduler\n\n✨ Features:\n- Production lines management\n- Orders scheduling\n- Interactive timeline\n- AI optimization\n- Real-time analytics\n\n📅 Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
				
				subprocess.run(["git", "commit", "-m", commit_message], check=True)
				print("✅ Initial commit created")
				
				# Adaugă remote
				remote_url = f"https://{self.github_token}@github.com/{self.github_username}/{self.repo_name}.git"
				subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
				print("✅ Remote origin added")
				
				# Push
				subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
				print("✅ Code pushed to GitHub successfully!")
				
				return True
				
			except Exception as e:
				print(f"❌ Failed to commit and push: {e}")
				return False

		def cleanup(self):
			"""Curăță fișierele temporare"""
			try:
				os.chdir("..")  # Ieși din directorul temp
				if os.path.exists(self.temp_repo_path):
					shutil.rmtree(self.temp_repo_path)
					print(f"🗑️ Cleaned up temp directory: {self.temp_repo_path}")
			except Exception as e:
				print(f"⚠️ Cleanup warning: {e}")

		def run(self):
			"""Rulează întregul proces de upload"""
			print("🚀 Starting GitHub upload process...\n")
			
			start_time = time.time()
			
			try:
				# 1. Verifică prerequisites
				if not self.check_prerequisites():
					return False
				
				# 2. Creează repo pe GitHub
				repo_info = self.create_github_repo()
				if not repo_info:
					return False
				
				# 3. Pregătește repo local
				if not self.prepare_local_repo(repo_info):
					return False
				
				# 4. Commit și push
				if not self.commit_and_push(repo_info):
					return False
				
				# 5. Success!
				elapsed_time = time.time() - start_time
				
				print(f"\n🎉 SUCCESS! Upload completed in {elapsed_time:.1f} seconds")
				print(f"🔗 Your repository is now live at:")
				print(f"   {repo_info['html_url']}")
				print(f"\n📋 Next steps:")
				print(f"   1. Visit your repository on GitHub")
				print(f"   2. Check the README.md for documentation")
				print(f"   3. Share with your team!")
				print(f"   4. Start collaborating! 🚀")
				
				return True
				
			except Exception as e:
				print(f"\n❌ Upload process failed: {e}")
				return False
			
			finally:
				# Cleanup
				self.cleanup()

	def main():
		"""Funcția principală"""
		print("="*60)
		print("🏭 MANUFACTURING PROJECT → GITHUB UPLOADER")
		print("="*60)
		
		# INSTRUCȚIUNI IMPORTANTE
		print("\n📋 BEFORE RUNNING:")
		print("1. Create a GitHub Personal Access Token:")
		print("   → Go to GitHub.com → Settings → Developer settings → Personal access tokens")
		print("   → Generate new token with 'repo' permissions")
		print("2. Update the script with your credentials:")
		print("   → github_username = 'your_actual_username'")
		print("   → github_token = 'your_actual_token'")
		print("\n⚠️  IMPORTANT: Keep your token secure and never share it!")
		
		# Confirmă că user-ul a citit instrucțiunile
		response = input("\n✅ Have you updated your credentials? (y/n): ").lower()
		if response != 'y':
			print("❌ Please update your credentials first!")
			return
		
		# Rulează upload-ul
		uploader = GitHubUploader()
		success = uploader.run()
		
		if success:
			print(f"\n🎊 CONGRATULATIONS! Your Manufacturing Project is now on GitHub! 🎊")
		else:
			print(f"\n💔 Upload failed. Check the errors above and try again.")

	if __name__ == "__main__":
		main()