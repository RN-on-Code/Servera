import pyautogui as pg 
boiler_html =  '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>

    <h1>Hello, World!</h1>
    
    <!-- Your content goes here -->

</body>
</html>
'''
for i in range(len(boiler_html)):
 pg.hotkey(boiler_html[i])

