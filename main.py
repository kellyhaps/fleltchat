import flet as ft
import requests
import json
from uuid import uuid4
from datetime import datetime


def main(page: ft.Page):
	# === main page settings =========================================================================================================;
	page.title = "Cloud Chat"
	#page.window.width = 400
	#page.window.height = 550

	#get full datalist;
	# - test to read data
	url="https://fletchat-73f82-default-rtdb.europe-west1.firebasedatabase.app/.json"
	base_url = "https://fletchat-73f82-default-rtdb.europe-west1.firebasedatabase.app/"
	auth_key = 'AIzaSyCvDmvyvBkQX4IhKUQHkZK0tSB3_TKUL2E'

	# === Log-in / registration page ========================================================
	# - functions for login/registration ---
	# - check user name ---
	def user_check(user_name):
		global current_user
		user_url = f"{base_url}users/{user_name}/.json"
		request = requests.get(user_url+'?auth='+auth_key)
		current_user = request.json()

	# - Login function ---
	def login(e):
		user_name = profiel_name.value
		user_pword = profiel_pword.value
		#check for user name excist
		user_check(user_name)
		if current_user == None:
			page.open(ft.SnackBar(ft.Text(f"{user_name} does not exist!"),bgcolor=ft.Colors.RED,))
			return
		#check if pasword is correct
		if current_user["Password"] != user_pword:
			page.open(ft.SnackBar(ft.Text(f"{user_name} got the wrong password!"),bgcolor=ft.Colors.ORANGE,))
			return
		#succesfully logged in;
		page.open(ft.SnackBar(ft.Text(f"{user_name} succesfully loged in!"),bgcolor=ft.Colors.GREEN,duration=500))
		page.session.set("login",True)
		page.clean()
		reload_program()
		main_top_lbl.value = f"Welcome {current_user['Username']}"
		page.update()
		

	# - registration function ---
	def registration(e):
		#get username and password
		user_name = profiel_name.value
		user_pword = profiel_pword.value
		#check if profile excist
		user_check(user_name)
		if current_user == None:
			#create url
			update_url = f"{base_url}/users.json"
			JSON = {user_name:{"Username":user_name,"Password":user_pword,"Connections":{"Add contacts":True}}}
			JSON = json.dumps(JSON)
			to_database = json.loads(JSON)
			requests.patch(url = update_url, json= to_database)
			#clear Widgets
			profiel_name.value = ""
			profiel_pword.value = ""
			page.update()
			page.open(ft.SnackBar(ft.Text(f"{user_name} succesfully registrated!"),bgcolor=ft.Colors.GREEN,))
		#profile already exist;
		page.open(ft.SnackBar(ft.Text(f"{user_name} already in use!"),bgcolor=ft.Colors.RED,))

	# - widgets for login/registration ---
	# - top label ---
	label_top = ft.Text( f"Welcome to CloudChat",size = 20 ,weight=ft.FontWeight.BOLD)
	# - username / password ---
	profiel_name = ft.TextField(expand=True,hint_text="Username", value="kly")
	profiel_pword = ft.TextField(expand=True,hint_text="Password",value="k", autofocus=True, on_submit=login)
	# -login / registerd ---
	login_btn = ft.ElevatedButton(text="Login",on_click=login)
	registration_btn = ft.ElevatedButton(text="Registrate",on_click=registration)

	# - put labels - for login.
	def login_scr():
		page.add(
				ft.Row([label_top]),
				ft.Row([profiel_name]),
				ft.Row([profiel_pword]),
				ft.Row([login_btn,registration_btn]),
		)

	# === Main page ==============================================================================
	# - Top label --
	main_top_lbl = ft.Text( f"Welcome",size = 20 ,weight=ft.FontWeight.BOLD)

	# --- contacts --------------------------------------------------------------------
	# - function to add contact ---
	
	# - get all contacts --
	def check_contacts(contact_added):
		global check_user
		all_user_url = f"{base_url}users/{contact_added}/.json"
		request = requests.get(all_user_url+'?auth='+auth_key)
		check_user = request.json() 

	# - check for dummy contact ---
	def dummy_contact():
		global check_dummy
		#check_dummy_url = f"https://fletchat-73f82-default-rtdb.europe-west1.firebasedatabase.app/users/Add contacts/.json"
		check_dummy_url =f"{base_url}users/{current_user["Username"]}/Connections/Add%20contacts/.json"
		request = requests.get(check_dummy_url+'?auth='+auth_key)
		check_dummy = request.json() 

	# add the person
	def ad_contact(e):
		# - get value --
		contact_added = connect_name.value
		# - check if contact exist ---
		check_contacts(contact_added)
		if check_user == None:
			page.open(ft.SnackBar(ft.Text(f"{contact_added} doesn't exist!"),bgcolor=ft.Colors.RED,))
			return
		# -- update user to database ---
		connection_url = f"{base_url}users/{current_user["Username"]}/Connections/.json"
		JSON = {contact_added:True}
		JSON = json.dumps(JSON)
		to_database = json.loads(JSON)
		requests.patch(url = connection_url, json= to_database)
		# - delete if dummy exist;
		dummy_contact()
		if check_dummy != None:
			delete_url = f"{base_url}/users/{current_user['Username']}/Connections/Add%20contacts.json"
			response = requests.delete(delete_url)
		# close if succesful
		contact_scr.open = False
		user_name=current_user["Username"]
		user_check(user_name)
		#get_contacts()
		#load_dropdown()
		#contact_scr.open = False
		page.close(contact_scr)
		page.open(ft.SnackBar(ft.Text(f"{contact_added} added!"),bgcolor=ft.Colors.GREEN,))
		page.update()
		drop_menu.options = get_contacts()
		drop_menu.update()
		page.update()
		#page.clean()
		#page.update()
		#reload_program()
		

	connect_name=ft.TextField(hint_text="Contact Name")

	contact_scr = ft.AlertDialog(
		title=ft.Text("Ad contact!"),   
		content=ft.Column([connect_name], tight=True),
		actions=[ft.ElevatedButton(text="Add Contact", on_click=ad_contact)],
		alignment=ft.alignment.center,
		#on_dismiss=lambda e: print("Dialog dismissed!"),
		title_padding=ft.padding.all(25),
		actions_alignment="end",
	)
	# -  ad icon button ---
	ad_contact_btn = ft.IconButton(icon=ft.Icons.ADD_CIRCLE,on_click=lambda e: page.open(contact_scr))

	# --- Creat dropdown menu ---------------------------------------------------------


	# - add to dropdownlist ---
	def get_contacts():
		options = []
		for contact in current_user["Connections"]:
			#get the first name as active name;
			try:
				global active_name
				if active_name == "":
					pass
			except:
				active_name = contact
			options.append(
				ft.DropdownOption(
					key=contact,
					content=ft.Row(
						controls=[
							ft.Text(contact),
							ft.Container(expand=True),
							#ft.IconButton(ft.Icons.DELETE,data=contact,on_click=del_contact, icon_size=20, alignment=ft.Alignment(1.0, 1.0)),
					],
				vertical_alignment=ft.CrossAxisAlignment.CENTER,
				),
			)
		)
		return options

	# - get selected user ---
	def dropdown_changed(e):
		global active_name
		active_name=drop_menu.value
		#clear messages
		messages.controls.clear()
		upload_msg()
		page.update()

	# - load dropdown ---
	def load_dropdown():
		#get first contact
		first_contact = current_user["Connections"]
		first_contact = first_contact
		for key, value in first_contact.items():
			first_contact=key
			break
		global drop_menu
		drop_menu = ft.Dropdown(enable_filter = True,
								expand = True, 
								editable=True, 
								label=first_contact, 
								options=get_contacts(),
								leading_icon=ft.Icons.SEARCH, 
								on_change=dropdown_changed
							)

	# - list view -
	messages = ft.ListView(expand=True,auto_scroll=True)

	# --- load message ----------------------------------------------------------------------------
	# - Define bubbles ---
	def bubble_me(msg: str, time:str):
			display = f"{msg} \n {time}"
			return ft.Row(
				alignment=ft.MainAxisAlignment.END,
				controls=[
					ft.Container(
						content=ft.Text(display),
						padding=10,
						bgcolor = ft.Colors.GREEN_900,
						border_radius=20,
						margin=ft.margin.only(left=5,right=5,top=5,bottom=5)
						)
				],
			)
	# - Define bubble other;
	def bubble_other(msg: str, time:str):
		display = f"{msg} \n {time}"
		return ft.Row(
			alignment=ft.MainAxisAlignment.START,
			controls=[
				ft.Container(
					content=ft.Text(display),
					padding=10,
					bgcolor = ft.Colors.BLUE_900,
					border_radius=20,
					margin=ft.margin.only(left=5,right=5,top=5,bottom=5)
					)
			],
		)
	
	# -- get message ---
	def load_messages():
		global msg_list
		# get current user and active user
		me_user = current_user["Username"]
		user_list = [me_user, active_name]
		user_list = sorted(user_list, key=lambda c: c.lower())
		# load messages
		load_msg_url = f"{base_url}chats/{user_list[0]}-{user_list[1]}.json"
		request = requests.get(load_msg_url+'?auth='+auth_key)
		load_msg_url = request.json()
		#get - messages 
		msg_list = []
		if load_msg_url != None:
			for key, value in load_msg_url.items():
				temp_item = {"Time":key,"from":value["from"],"msg":value["msg"]}
				msg_list.append(temp_item)
	
	#put message on screen;
	def upload_msg():
		load_messages()
		for x in msg_list:
			#messages.controls.append(ft.Text(f"{x['msg']}"))
			#chek if its from me;
			if x['from'] == current_user['Username']:
				messages.controls.append(
					bubble_me(msg=(x['msg']), time=(x['Time'])))
			else:
				messages.controls.append(
					bubble_other(msg=(x['msg']), time=(x['Time'])))

	# --- function to send message -----------------------------------------------------------------
	#get time funtion
	def get_now()-> str:
		return str(datetime.now())[:19]

	# - send message ---
	def send_message(e):
		#get text
		input_msg = chat_box.value.strip()
		if not input_msg:
			return
		#clear inbox field
		chat_box.value=""
		# - save message to database -
		from_msg = [current_user["Username"],active_name]
		from_msg = sorted(from_msg, key=lambda c: c.lower())
		from_msg = str(from_msg)
		time = get_now()
		from_msg = from_msg.replace("[","")
		from_msg = from_msg.replace("]","")
		from_msg = from_msg.replace(",","-")
		from_msg = from_msg.replace("'","")
		from_msg = from_msg.replace(" ","")
		msg = {"msg":input_msg,"from":current_user["Username"]}
		#msg_url = f"{base_url}/chats/{from_msg}/.json"
		msg_url= f"{base_url}chats/{from_msg}/{time}.json"
		JSON = json.dumps(msg)
		to_database = json.loads(JSON)
		requests.put(url = msg_url, json= to_database)
		# put message to screen;
		messages.controls.clear()
		upload_msg()
		page.update()


	# - chatbox -
	chat_box = ft.TextField(expand=True,hint_text="Type your message",on_submit=send_message,autofocus=True)
	send_button = ft.IconButton(icon=ft.Icons.SEND,on_click=send_message)

	#temp reload button
	def reload_msg(e):
		messages.controls.clear()
		upload_msg()
		page.update()

	#button
	reload_button = ft.IconButton(icon=ft.Icons.REFRESH,on_click=reload_msg)

	# - put labels - for main screen
	def main_scr():
		page.add(
				ft.Row([main_top_lbl]),
				ft.Row([drop_menu,ad_contact_btn,reload_button]),
				messages,
				ft.Row([chat_box,send_button]),
		)

	# === Reload program ==============================================================================
	def reload_program():
		if page.session.get("login") == True:
			#main_content()
			load_dropdown()
			upload_msg()
			main_scr()
		#function to test if we have a login.
		if page.session.get("login") != True:
			login_scr()

	#to start;
	reload_program()



#-for local
#ft.app(main)
#for render
ft.app(target=main, view=ft.WEB_BROWSER)

# to deploy
#flet publish

#C:\Users\KellyvanMil\Documents\Python\Flet\cloudchat\src>flet build web

#poging om het klein te houden;
#flet build web --web-renderer html
#flet publish --web-renderer html

#C:\Users\KellyvanMil\Documents\Python\Flet\fletchat\src
#flet publish main.py --web-renderer html
