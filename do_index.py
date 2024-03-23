with open("./discussion.dat", "r") as discussion_file: discussion = discussion_file.read()
with open("./index.html.template", "r") as template_file: template = template_file.read()
with open("./index.html", "w") as fp:
    fp.write(template.replace("{DISCUSSION}", discussion))
    
        
