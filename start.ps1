conda activate pypy

$env:DEBUG="auto_derby"
$env:AUTO_DERBY_LAST_SCREENSHOT_SAVE_PATH="debug/last_screenshot.png"
$env:AUTO_DERBY_OCR_IMAGE_PATH="debug/ocr_images"
$env:AUTO_DERBY_SINGLE_MODE_EVENT_IMAGE_PATH="debug/single_mode_event_images"
$env:AUTO_DERBY_SINGLE_MODE_TRAINING_IMAGE_PATH="debug/single_mode_training_images"
$env:AUTO_DERBY_SINGLE_MODE_CHOICE_PATH="D:\dev\auto-derby\data\single_mode_choices.csv"
$env:AUTO_DERBY_PAUSE_IF_RACE_ORDER_GT="5"
$env:AUTO_DERBY_PLUGINS="limited_sale_buy_first_3,bluestacks_port,more_g1,race_campaign,debug_to_log,afk"
$env:AUTO_DERBY_SINGLE_MODE_TARGET_TRAINING_LEVELS="5,3,3,,"
$env:AUTO_DERBY_ADB_ADDRESS="127.0.0.1::D:\\Program Files\\BlueStacks_nxt\\bluestacks.conf"
$env:AUTO_DERBY_CHECK_UPDATE="true"

python -m auto_derby nurturing
