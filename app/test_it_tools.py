from tools.server_tools import check_server_status, reset_password


print("Authentication:")
print(check_server_status.invoke({}))

print("\nPassword:")
print(reset_password.invoke({}))