import os
import shutil
import subprocess
import zipfile
import platform
from datetime import datetime

from odoo import models, fields, http
from odoo.http import request
from odoo.exceptions import UserError
from odoo.tools import config


class DatabaseBackupWizard(models.TransientModel):
    _name = 'database.backup.wizard'
    _description = 'Database Backup Wizard'

    zip_path = fields.Char(string="Zip Path")
    file_name = fields.Char(string="File Name")

    def action_backup_database(self):
        db_name = self.env.cr.dbname

        db_user = config.get('db_user') or 'postgres'
        db_password = config.get('db_password') or ''
        db_host = config.get('db_host') or 'localhost'
        db_port = str(config.get('db_port') or '5432')

        pg_dump_path = shutil.which("pg_dump")

        if not pg_dump_path and platform.system() == "Windows":
            possible_paths = [
                r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
                r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
                r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe",
            ]
            for path in possible_paths:
                if os.path.isfile(path):
                    pg_dump_path = path
                    break

        if not pg_dump_path:
            raise UserError("pg_dump not found.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if platform.system() == "Windows":
            backup_root = os.path.join(os.path.expanduser("~"), "Downloads")
        else:
            backup_root = "/tmp/odoo_backups"

        os.makedirs(backup_root, exist_ok=True)

        temp_backup_dir = os.path.join(
            backup_root,
            "%s_backup_%s" % (db_name, timestamp)
        )
        os.makedirs(temp_backup_dir, exist_ok=True)

        dump_file = os.path.join(temp_backup_dir, "database.dump")

        env = os.environ.copy()
        if db_password:
            env["PGPASSWORD"] = db_password

        command = [
            pg_dump_path,
            "-h", db_host,
            "-p", db_port,
            "-U", db_user,
            "-F", "c",
            "-b",
            "-v",
            "-f", dump_file,
            db_name,
        ]

        result = subprocess.run(
            command,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise UserError("Database backup failed:\n%s" % result.stderr)

        # Filestore backup: images, attachments, documents
        if platform.system() == "Windows":
            filestore_path = r"C:\Users\Gowtham\Desktop\home\ubuntu\.local\share\Odoo\filestore\%s" % db_name
        else:
            filestore_path = os.path.expanduser(
                "~/.local/share/Odoo/filestore/%s" % db_name
            )

        if os.path.exists(filestore_path):
            shutil.copytree(
                filestore_path,
                os.path.join(temp_backup_dir, "filestore"),
                dirs_exist_ok=True,
            )
        else:
            raise UserError("Filestore not found:\n%s" % filestore_path)

        # Custom addon backup
        if platform.system() == "Windows":
            addon_path = r"C:\odoo\custom_addons\SICAWeb-main\member_management_system"
        else:
            addon_path = "/opt/odoo15/SICAWeb/member_management_system"

        if os.path.exists(addon_path):
            shutil.copytree(
                addon_path,
                os.path.join(temp_backup_dir, "member_management_system"),
                dirs_exist_ok=True,
            )

        # Odoo config backup
        if platform.system() == "Windows":
            config_path = r"C:\odoo\custom_addons\SICAWeb-main\muthu-odoo.conf"
        else:
            config_path = "/etc/odoo.conf"

        if os.path.exists(config_path):
            shutil.copy2(
                config_path,
                os.path.join(temp_backup_dir, "odoo.conf")
            )

        file_name = "%s_full_backup_%s.zip" % (db_name, timestamp)
        zip_file = os.path.join(backup_root, file_name)

        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_backup_dir)
                    zipf.write(file_path, arcname)

        shutil.rmtree(temp_backup_dir, ignore_errors=True)

        self.write({
            "zip_path": zip_file,
            "file_name": file_name,
        })

        return {
            "type": "ir.actions.act_url",
            "url": "/database_backup/download/%s" % self.id,
            "target": "self",
        }


class DatabaseBackupDownloadController(http.Controller):

    @http.route('/database_backup/download/<int:wizard_id>', type='http', auth='user')
    def download_backup(self, wizard_id, **kw):
        wizard = request.env['database.backup.wizard'].sudo().browse(wizard_id)

        if not wizard.exists() or not wizard.zip_path:
            return request.not_found()

        if not os.path.exists(wizard.zip_path):
            return request.not_found()

        file_name = wizard.file_name or os.path.basename(wizard.zip_path)
        file_size = os.path.getsize(wizard.zip_path)

        with open(wizard.zip_path, 'rb') as backup_file:
            file_data = backup_file.read()

        return request.make_response(
            file_data,
            headers=[
                ('Content-Type', 'application/zip'),
                ('Content-Disposition', 'attachment; filename="%s"' % file_name),
                ('Content-Length', str(file_size)),
            ]
        )