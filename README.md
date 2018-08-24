# Бот Telegram для получения перлов нейросетевого перевода Google Translate

Создано просто ради рофла.

## Установка
```
cd ~
wget https://github.com/vslvcode/google_neuro/archive/master.zip
unzip master.zip
cd google_neuro-master
pip3 install -r requirements.txt
```

## Запуск

### Базовый функционал
```
cd ~/google_neuro-master/app
python3 main.py -t токен_вашего_бота
```

### С функцией репоста в канал
Бот должен быть назначен администратором канала.
```
cd ~/google_neuro-master/app
python3 main.py -t токен_вашего_бота -c ваш_канал -a user_id_администратора
```

Для включения записи логов добавьте ```-l```.

## Обновление
```
cd ~/google_neuro-master
./update.sh
```

Перед первым запуском ```update.sh``` нужно задать права на исполнение.
```
chmod +x update.sh
```
