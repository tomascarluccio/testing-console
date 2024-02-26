import os
import re
import shutil

import requests
from flask import Flask, render_template, send_file, request, redirect, jsonify, send_from_directory
from requests.auth import HTTPBasicAuth

import config

# TODO:
# solo acepta 1 email

app = Flask(__name__)

app.config.from_object('config.OcDev')

XML_DIR = 'static/xml'
XML_FILENAME = 'testng.xml'

config_class = config.OcDev
DRY_MODE = config_class.DRY_MODE
TENANT_NAME = config_class.TENANT_NAME
TENANT_URL = config_class.TENANT_URL
TN_USERNAME = config_class.TN_USERNAME
TN_PASSWORD = config_class.TN_PASSWORD
OC_HOST = config_class.OC_HOST
OC_0AUTH2_TOKEN = config_class.OC_0AUTH2_TOKEN
EXTERNAL_TESTNG_TN = config_class.EXTERNAL_TESTNG_TN
JENKINS_TOKEN = config_class.JENKINS_TOKEN

jenkins_user = "altipeak"
jenkins_password = "118a332880711412dc7299c079598777ae"


def get_versions():
    url = "https://" + app.config['OC_HOST'] + ":8443/api/v1/multitenancy/appliance_version/"
    headers = {"Authorization": "Bearer " + app.config['OC_0AUTH2_TOKEN']}
    response = requests.get(url, headers=headers)
    data = response.json().get("results")

    versions = []
    stable_version = ""
    for item in data:
        version = item.get("version") + " (" + item.get("status") + ")"
        if version:
            versions.append(version)

        if item.get("status") == "0-STABLE":
            stable_version = version

    return versions, stable_version


def is_in_progress():
    url_mt = "https://jenkins.dev.safewalk.info/job/safewalk-testing-suite/lastBuild/api/json"
    url_v5 = "https://jenkins.dev.safewalk.info/job/Safewalk-v5-TestSuite/lastBuild/api/json"

    try:
        response_mt = requests.get(url_mt, auth=HTTPBasicAuth(jenkins_user, jenkins_password))
        response_mt.raise_for_status()  # Lanza una excepción para errores HTTP (p. ej., 404, 500)
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud HTTP: {e}")
        return "ERROR: Could not connect to Jenkins"

    try:
        response_v5 = requests.get(url_v5, auth=HTTPBasicAuth(jenkins_user, jenkins_password))
        response_v5.raise_for_status()  # Lanza una excepción para errores HTTP (p. ej., 404, 500)
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud HTTP: {e}")
        return "ERROR: Could not connect to Jenkins"

    if response_mt.json().get("timestamp") > response_v5.json().get("timestamp"):
        return [response_mt.json().get("inProgress"), "mt"]
    else:
        return [response_v5.json().get("inProgress"), "v5"]

def get_result():
    url = "https://jenkins.dev.safewalk.info/job/safewalk-testing-suite/lastBuild/api/json"

    response = requests.get(url, auth=HTTPBasicAuth(jenkins_user, jenkins_password))
    return response.json().get("result")


def modify_string(string):
    string = re.sub(r'\s', '%20', string)
    string = re.sub(r'\(', r'\\(', string)
    string = re.sub(r'\)', r'\\)', string)
    return string

def limit_results(limit, path):
    try:
        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

        if len(folders) <= limit:
            return

        folders = sorted(folders, key=lambda folder: os.path.getctime(os.path.join(path, folder)))

        num_to_delete = len(folders) - limit

        for i in range(num_to_delete):
            folder_to_delete = os.path.join(path, folders[i])
            try:
                shutil.rmtree(folder_to_delete)
            except Exception as e:
                print(f"Could not delete folder {folder_to_delete}: {e}")
    except Exception as e:
        return f"Error processing path {path}: {e}"



@app.route("/", methods=['POST', 'GET'])
def dashboard():
    limit_results(20, "reports")

    try:
        versions = get_versions()
    except:
        return "ERROR: Could not connect to Orchestrator", 500

    stable_version = versions[1]
    if request.method == 'POST' and request.form:
        target_version = request.form.get('selected_version')
        email_recipients = request.form.get('inputMail')
        platform = request.form.get('platform')
        dev_switch = request.form.get('devSwitch')
        oc_ui = request.form.get('ocUi')
        tnt_ui = request.form.get('tntUi')
        auth_api = request.form.get('authApi')
        auth_radius = request.form.get('authRadius')
        postman_oc = request.form.get('postmanOc')
        postman_tnt = request.form.get('postmanTnt')

        if email_recipients and not re.match(r"[^@]+@[^@]+\.[^@]+", email_recipients):
            return redirect(request.url)

        if is_in_progress()[0]:
            return redirect(request.url)


        if platform == "multitenancy":
            if dev_switch == "false":
                branch = "merge"
            else:
                branch = "beta"
            command = f'curl -I -u {jenkins_user}:{jenkins_password} "https://jenkins.dev.safewalk.info/job/safewalk-testing-suite/buildWithParameters?token={JENKINS_TOKEN}&DRY_MODE={DRY_MODE}&EXTERNAL_TESTNG_TN={EXTERNAL_TESTNG_TN}&STABLE_VERSION={modify_string(stable_version)}&TARGET_VERSION={modify_string(target_version)}&TENANT_NAME={TENANT_NAME}&TENANT_URL={TENANT_URL}&TN_USERNAME={TN_USERNAME}&TN_PASSWORD={TN_PASSWORD}&OC_HOST={OC_HOST}&OC_0AUTH2_TOKEN={OC_0AUTH2_TOKEN}&EMAIL_RECIPIENTS={email_recipients}&PLATFORM={branch}&OC_UI={oc_ui}&TNT_UI={tnt_ui}&AUTH_API={auth_api}&AUTH_RADIUS={auth_radius}&POSTMAN_OC={postman_oc}&POSTMAN_TNT={postman_tnt}"'
        else:
            if dev_switch == "false":
                branch = "merge"
            else:
                branch = "beta"
            command = f'curl -I -u {jenkins_user}:{jenkins_password} "https://jenkins.dev.safewalk.info/job/Safewalk-v5-TestSuite/buildWithParameters?token={JENKINS_TOKEN}&DRY_MODE={DRY_MODE}&EXTERNAL_TESTNG_TN={EXTERNAL_TESTNG_TN}&STABLE_VERSION={modify_string(stable_version)}&TARGET_VERSION={modify_string(target_version)}&TENANT_NAME={TENANT_NAME}&TENANT_URL={TENANT_URL}&TN_USERNAME={TN_USERNAME}&TN_PASSWORD={TN_PASSWORD}&OC_HOST={OC_HOST}&OC_0AUTH2_TOKEN={OC_0AUTH2_TOKEN}&EMAIL_RECIPIENTS={email_recipients}&PLATFORM={branch}&OC_UI={oc_ui}&TNT_UI={tnt_ui}&AUTH_API={auth_api}&AUTH_RADIUS={auth_radius}&POSTMAN_OC={postman_oc}&POSTMAN_TNT={postman_tnt}"'

        os.system(command)


    inProgress = is_in_progress()[0]
    inProgressPlatform = is_in_progress()[1]
    result = get_result()

    reports = get_reports()
    return render_template('dashboard.html', versions=versions[0], isInProgress=inProgress, inProgressPlatform=inProgressPlatform, result=result, reports=reports)


def get_reports():
    reports_folder_content = os.listdir('reports')
    reports_folder_content = sorted(reports_folder_content, key=lambda folder: os.path.getctime(os.path.join("reports", folder)))
    reports_folder_content.reverse()

    reports = []
    for report_folder in reports_folder_content:
        folder_name = report_folder
        report = []
        subreports = os.listdir(f'reports/{report_folder}')
        ui_report = ""
        troubleshootingList = []
        orchestrator_postman = ""
        tenant_postman = ""

        for subreport in subreports:
            if subreport == "ui":
                if os.listdir(f'reports/{report_folder}/ui'):
                    ui_report = os.listdir(f'reports/{report_folder}/ui')[0]
            elif subreport == "troubleshooting":
                troubleshooting_files = os.listdir(f'reports/{report_folder}/troubleshooting')
                if troubleshooting_files:
                    for troublshooting_package in troubleshooting_files:
                        troubleshootingList.append(troublshooting_package)
            elif subreport == "postman":
                postman_subfolders = os.listdir(f'reports/{report_folder}/postman')
                for postman_subfolder in postman_subfolders:
                    if postman_subfolder == "orchestrator":
                        if os.listdir(f'reports/{report_folder}/postman/orchestrator'):
                            orchestrator_postman = os.listdir(f'reports/{report_folder}/postman/orchestrator')[0]
                    elif postman_subfolder == "tenant":
                        if os.listdir(f'reports/{report_folder}/postman/tenant'):
                            tenant_postman = os.listdir(f'reports/{report_folder}/postman/tenant')[0]

        report.append(folder_name)
        report.append(ui_report)
        report.append(orchestrator_postman)
        report.append(tenant_postman)
        report.append(troubleshootingList)
        reports.append(report)
    return reports


@app.route('/reports/<report_folder>/ui/<filename>')
def load_ui_page(report_folder, filename):
    file_path = f'reports/{report_folder}/ui/{filename}'
    try:
        return send_file(file_path)
    except FileNotFoundError:
        return f"File {filename} not found", 404


@app.route('/reports/<report_folder>/postman/orchestrator/<filename>')
def load_postman_page_orchestrator(report_folder, filename):
    file_path = f'reports/{report_folder}/postman/orchestrator/{filename}'
    try:
        return send_file(file_path)
    except FileNotFoundError:
        return f"File {filename} not found", 404


@app.route('/reports/<report_folder>/postman/tenant/<filename>')
def load_postman_page_tenant(report_folder, filename):
    file_path = f'reports/{report_folder}/postman/tenant/{filename}'
    try:
        return send_file(file_path)
    except FileNotFoundError:
        return f"File {filename} not found", 404

@app.route('/reports/<report_folder>/troubleshooting/<filename>')
def download_file(report_folder, filename):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_directory, 'reports', report_folder, 'troubleshooting', filename)
    return send_file(file_path, as_attachment=True)


@app.route('/get_task_status')
def get_task_status():
    task_in_progress = is_in_progress()[0]
    return jsonify({'isInProgress': task_in_progress})

@app.route('/get_task_result')
def get_task_result():
    task_result = get_result()
    return jsonify({'taskResult': task_result})

@app.route('/abort_build', methods=['POST'])
def abort_build():
    get_build_number = "https://jenkins.dev.safewalk.info/job/safewalk-testing-suite/lastBuild/buildNumber"

    try:
        response = requests.post(get_build_number, auth=(jenkins_user, jenkins_password))
        response.raise_for_status()
        build_number = response.content.decode("utf-8")

        stop_build = f"https://jenkins.dev.safewalk.info/job/safewalk-testing-suite/{build_number}/stop"
        response2 = requests.post(stop_build, auth=(jenkins_user, jenkins_password))

        return jsonify({"message": "Build aborted successfully"})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to abort build", "details": str(e)})
