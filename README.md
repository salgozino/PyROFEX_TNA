# PyROFEX_TNA
Analizador de la Tasa implícita en tiempo real sobre los futuros ROFEX

Utilizando la API de Rofex se leen los datos en tiempo real del precio del indice ROFX20 y del futuro, en este caso Septiembre, pero se puede cambiar el futuro a analizar. Además se debe especificar la fecha de vencimiento de dicho futuro. Con ello, el código calcula la Tasa Implícita de cada punta (BI, OF y LA) y las grafica en tiempo real cada 3 segundos (también se puede modificar este tiempo).
