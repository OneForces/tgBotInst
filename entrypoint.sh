#!/bin/bash

rm -f /tmp/.X0-lock

echo "[🚀] Запуск виртуального экрана..."
Xvfb :0 -screen 0 1280x720x24 &
export DISPLAY=:0

echo "[🎨] Запуск оконного менеджера..."
fluxbox &

echo "[📱] Запуск Android эмулятора..."
$ANDROID_SDK_ROOT/emulator/emulator -avd test -no-audio -no-window -no-boot-anim -gpu swiftshader_indirect -no-snapshot -read-only &
EMULATOR_PID=$!

echo "[⏳] Ожидание эмулятора..."
$ANDROID_SDK_ROOT/platform-tools/adb wait-for-device

# ✅ Ждём boot_completed
echo "[⏳] Ждём полной загрузки системы..."
boot_completed=""
while [[ "$boot_completed" != "1" ]]; do
    boot_completed=$($ANDROID_SDK_ROOT/platform-tools/adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')
    sleep 1
done

echo "[✅] Устройство готово, запускаем Appium..."
exec appium --address 0.0.0.0 --port 4723 --base-path /wd/hub --log-level info
