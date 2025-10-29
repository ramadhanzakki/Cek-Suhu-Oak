import csv

def input_temp():
  while True:
    try:
      suhu = int(input('Masukan suhu: '))
      break
    except ValueError:
      print('Input tidak valid')
      continue
  return suhu

def suhu_csv():
  with open('input.csv', 'r') as file:
    data = file.readlines()
  return data