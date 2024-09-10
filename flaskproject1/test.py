from werkzeug.security import generate_password_hash, check_password_hash

hashed_password = generate_password_hash('Adm1n@Fl2sk', method='pbkdf2:sha256', salt_length=16)
print(hashed_password)


final = check_password_hash('pbkdf2:sha256:600000$rcZ0iBuM76WAWjdm$d0d4fe93f61f0d7eb69421cf164123b7a0f66201af7c57c740bb8cd01be184a1', 'Adm1n@Fl2sk')
print(final)

