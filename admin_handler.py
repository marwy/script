from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.models import User, Skin, Collection
from filters.admin_filter import AdminFilter
from utils.inventory import add_skin_to_inventory, get_user_inventory
from typing import Union

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminStates(StatesGroup):
    choosing_action = State()
    adding_collection = State()
    adding_collection_type = State()
    adding_collection_description = State()
    adding_collection_price = State()
    adding_collection_folder = State()
    choosing_collection = State()
    adding_skin_name = State()
    adding_skin_description = State()
    adding_skin_photo = State()
    adding_skin_chance = State()
    editing_collection = State()
    editing_collection_name = State()
    editing_collection_type = State()
    editing_collection_description = State()
    editing_collection_price = State()
    editing_collection_active_from = State()
    editing_collection_active_to = State()
    editing_skin = State()
    editing_skin_name = State()
    editing_skin_description = State()
    editing_skin_photo = State()
    editing_skin_chance = State()

async def admin_handler(message: Message):
    await message.answer('Вы админ')


async def add_item_handler(message: Message):
    command_parts = message.text.split()
    if len(command_parts) != 3:
        await message.answer("Неправильный формат команды. Используйте /hack skin_id кол")
        return
    
    item_id = command_parts[1]
    quantity = command_parts[2]
    
    if not item_id.isnumeric() or not quantity.isnumeric():
        await message.answer("Неправильный формат команды. Используйте /hack skin_id(число) кол(число)")
        return
    
    user = await User.get(id=message.from_user.id)
    skin = await Skin.get(item_id=int(item_id))
    
    for _ in range(int(quantity)):
        await add_skin_to_inventory(user, skin)
    
    await message.answer(f'Предмет с id {item_id} добавлен в инвентарь в количестве {quantity}')

    # Показать обновленный инвентарь
    inventory = await get_user_inventory(user.id)
    inventory_text = f"Обновленный инвентарь пользователя {inventory['username']}:\n"
    for item in inventory['inventory']:
        inventory_text += f"{item['skin_name']} из коллекции {item['collection_name']} - {item['count']} шт.\n"
    
    await message.answer(inventory_text)

async def admin_menu(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    logger.info("Вызвана функция admin_menu")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить коллекцию", callback_data="admin_add_collection")],
        [InlineKeyboardButton(text="Добавить скин", callback_data="admin_add_skin")],
        [InlineKeyboardButton(text="Редактировать коллекцию", callback_data="admin_edit_collections")],
        [InlineKeyboardButton(text="Редактировать скин", callback_data="admin_edit_skin")],
        [InlineKeyboardButton(text="Просмотреть все коллекции", callback_data="admin_view_collections")]
    ])
    
    if isinstance(message, types.Message):
        await message.answer("Выберите действие:", reply_markup=keyboard)
    else:  # CallbackQuery
        await message.message.edit_text("Выберите действие:", reply_markup=keyboard)
    
    await state.set_state(AdminStates.choosing_action)

async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"Вызвана функция process_callback с данными: {callback_query.data}")
    action = callback_query.data
    
    if action in ["admin_add_collection", "admin_add_skin", "admin_edit_collections", "admin_edit_skin", "admin_view_collections"]:
        if action == "admin_add_collection":
            await callback_query.message.answer("Введите название новой коллекции:")
            await state.set_state(AdminStates.adding_collection)
        elif action == "admin_add_skin":
            collections = await Collection.all()
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=c.name, callback_data=f"admin_collection_{c.id}")] for c in collections
            ])
            await callback_query.message.answer("Выберите коллекцию для нового скина:", reply_markup=keyboard)
            await state.set_state(AdminStates.choosing_collection)
        elif action == "admin_edit_collections":
            await show_collections_for_edit(callback_query, state)
        elif action == "admin_edit_skin":
            await show_collections_for_skin_edit(callback_query, state)
        elif action == "admin_view_collections":
            collections = await Collection.all().prefetch_related('skins')
            for collection in collections:
                skins = [f"- {skin.name}" for skin in collection.skins]
                skins_text = "\n".join(skins) if skins else "Нет скинов"
                await callback_query.message.answer(
                    f"Коллекция: {collection.name}\n"
                    f"Тип: {collection.type}\n"
                    f"Описание: {collection.description}\n"
                    f"Цена крафта: {collection.price_craft}\n"
                    f"Скины:\n{skins_text}"
                )
        await callback_query.answer()
    else:
        # Пропускаем обработку других callback-запросов
        return

async def show_collections_for_edit(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info("show_collections_for_edit вызван")
    collections = await Collection.all()
    keyboard = InlineKeyboardBuilder()
    for c in collections:
        keyboard.button(text=c.name, callback_data=f"admin_collection_edit_{c.id}")
    keyboard.button(text="Назад", callback_data="admin_menu_back")
    keyboard.adjust(2)
    await callback_query.message.edit_text("Выберите коллекцию для редактирования:", reply_markup=keyboard.as_markup())
    await callback_query.answer()

async def edit_collection(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"edit_collection вызван с данными: {callback_query.data}")
    collection_id = int(callback_query.data.split('_')[3])
    await show_edit_collection_menu(callback_query.message, state, collection_id)
    await callback_query.answer()

async def show_edit_collection_menu(message: types.Message, state: FSMContext, collection_id: int):
    collection = await Collection.get(id=collection_id)
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Изменить название", callback_data=f"admin_collection_field_edit_name_{collection_id}")
    keyboard.button(text="Изменить тип", callback_data=f"admin_collection_field_edit_type_{collection_id}")
    keyboard.button(text="Изменить описание", callback_data=f"admin_collection_field_edit_description_{collection_id}")
    keyboard.button(text="Изменить цену крафта", callback_data=f"admin_collection_field_edit_price_{collection_id}")
    keyboard.button(text="Изменить дату начала", callback_data=f"admin_collection_field_edit_active_from_{collection_id}")
    keyboard.button(text="Изменить дату окончания", callback_data=f"admin_collection_field_edit_active_to_{collection_id}")
    keyboard.button(text="Удалить коллекцию", callback_data=f"admin_collection_delete_{collection_id}")
    keyboard.button(text="Назад к списку коллекций", callback_data="admin_edit_collections")
    keyboard.adjust(2)
    
    await message.answer(f"Редактирование коллекции '{collection.name}':", reply_markup=keyboard.as_markup())
    await state.set_state(AdminStates.editing_collection)

async def edit_collection_field(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"edit_collection_field вызван с данными: {callback_query.data}")
    parts = callback_query.data.split('_')
    field = parts[4]
    collection_id = int(parts[-1])  # Изменено: берем последний элемент как id
    await state.update_data(editing_collection_id=collection_id, editing_field=field)
    
    if field == "name":
        await state.set_state(AdminStates.editing_collection_name)
        await callback_query.message.edit_text("Введите новое название коллекции:")
    elif field == "type":
        await state.set_state(AdminStates.editing_collection_type)
        await callback_query.message.edit_text("Введите новый тип коллекции (permanent, seasonal, event):")
    elif field == "description":
        await state.set_state(AdminStates.editing_collection_description)
        await callback_query.message.edit_text("Введите новое описание коллекции:")
    elif field == "price":
        await state.set_state(AdminStates.editing_collection_price)
        await callback_query.message.edit_text("Введите новую цену крафта:")
    elif field == "active":
        if parts[5] == "from":
            await state.set_state(AdminStates.editing_collection_active_from)
            await callback_query.message.edit_text("Введите новую дату начала (формат: ГГГГ-ММ-ДД ЧЧ:ММ):")
        elif parts[5] == "to":
            await state.set_state(AdminStates.editing_collection_active_to)
            await callback_query.message.edit_text("Введите новую дату окончания (формат: ГГГГ-ММ-ДД ЧЧ:ММ):")
    
    await callback_query.answer()

async def delete_collection(callback_query: types.CallbackQuery, state: FSMContext):
    collection_id = int(callback_query.data.split('_')[3])
    collection = await Collection.get(id=collection_id)
    await collection.delete()
    await callback_query.answer("Коллекция успешно удалена!")
    await show_collections_for_edit(callback_query, state)

async def save_edited_collection(message: Message, state: FSMContext):
    data = await state.get_data()
    collection_id = data['editing_collection_id']
    field = data['editing_field']
    
    collection = await Collection.get(id=collection_id)
    
    if field == "name":
        collection.name = message.text
    elif field == "type":
        if message.text.lower() not in ['permanent', 'seasonal', 'event']:
            await message.answer("Неверный тип. Пожалуйста, выберите из: permanent, seasonal, event")
            return
        collection.type = message.text.lower()
    elif field == "description":
        collection.description = message.text
    elif field == "price":
        if not message.text.isdigit():
            await message.answer("Пожалуйста, введите число для цены крафта.")
            return
        collection.price_craft = int(message.text)
    elif field in ["active_from", "active_to"]:
        try:
            date = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
            setattr(collection, field, date)
        except ValueError:
            await message.answer("Неверный формат даты. Используйте формат: ГГГГ-ММ-ДД ЧЧ:ММ")
            return
    
    await collection.save()
    await message.answer(f"Коллекция успешно обновлена!")
    
    # Возвращаемся в меню редактирования коллекции
    await show_edit_collection_menu(message, state, collection_id)

async def add_collection(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите тип коллекции (permanent, seasonal, event):")
    await state.set_state(AdminStates.adding_collection_type)

async def add_collection_type(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['permanent', 'seasonal', 'event']:
        await message.answer("Неверный тип. Пожалуйста, выберите из: permanent, seasonal, event")
        return
    await state.update_data(type=message.text.lower())
    await message.answer("Введите описание коллекции:")
    await state.set_state(AdminStates.adding_collection_description)

async def add_collection_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите цену крафта:")
    await state.set_state(AdminStates.adding_collection_price)

async def add_collection_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число для цены крафта.")
        return
    await state.update_data(price_craft=int(message.text))
    await message.answer("Введите имя папки для скинов:")
    await state.set_state(AdminStates.adding_collection_folder)

async def finish_adding_collection(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data['folder_name'] = message.text
    new_collection = await Collection.create(**data)
    await message.answer(f"Коллекция '{new_collection.name}' успешно добавлена!")
    await state.clear()

async def choose_collection_for_skin(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"choose_collection_for_skin вызван с данными: {callback_query.data}")
    collection_id = int(callback_query.data.split('_')[2])
    await state.update_data(collection_id=collection_id)
    await callback_query.message.answer("Введите название нового скина:")
    await state.set_state(AdminStates.adding_skin_name)
    await callback_query.answer()

async def add_skin_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание скина:")
    await state.set_state(AdminStates.adding_skin_description)

async def add_skin_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите имя файла фото скина:")
    await state.set_state(AdminStates.adding_skin_photo)

async def add_skin_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.text)
    await message.answer("Введите шанс выпадения скина (например, B - 80%):")
    await state.set_state(AdminStates.adding_skin_chance)

async def finish_adding_skin(message: types.Message, state: FSMContext):
    await state.update_data(chance=message.text)
    data = await state.get_data()
    collection = await Collection.get(id=data['collection_id'])
    new_skin = await Skin.create(collection=collection, **data)
    await message.answer(f"Скин '{new_skin.name}' успешно добавлен в коллекцию '{collection.name}'!")
    await state.clear()

async def show_collections_for_skin_edit(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info("show_collections_for_skin_edit вызван")
    collections = await Collection.all()
    keyboard = InlineKeyboardBuilder()
    for c in collections:
        keyboard.button(text=c.name, callback_data=f"admin_edit_skin_collection_{c.id}")
    keyboard.button(text="Назад", callback_data="admin_menu_back")
    keyboard.adjust(2)
    
    await callback_query.message.edit_text("Выберите коллекцию скина для редактирования:", reply_markup=keyboard.as_markup())
    await callback_query.answer()

async def edit_skin_collection(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"edit_skin_collection вызван с данными: {callback_query.data}")
    if callback_query.data.startswith("admin_edit_skin_collection_"):
        collection_id = int(callback_query.data.split('_')[4])
    else:
        collection_id = int(callback_query.data.split('_')[3])
    
    collection = await Collection.get(id=collection_id).prefetch_related('skins')
    
    keyboard = InlineKeyboardBuilder()
    for skin in collection.skins:
        keyboard.button(text=skin.name, callback_data=f"admin_edit_skin_{skin.item_id}")
    keyboard.button(text="Назад к списку коллекций", callback_data="admin_edit_collections")
    keyboard.adjust(2)
    
    await callback_query.message.edit_text(f"Выберите скин для редактирования из коллекции '{collection.name}':", reply_markup=keyboard.as_markup())
    await callback_query.answer()

async def edit_skin(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"edit_skin вызван с данными: {callback_query.data}")
    skin_id = int(callback_query.data.split('_')[3])
    await show_edit_skin_menu(callback_query.message, state, skin_id)
    await callback_query.answer()

async def show_edit_skin_menu(message: types.Message, state: FSMContext, skin_id: int):
    skin = await Skin.get(item_id=skin_id)
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Изменить название", callback_data=f"admin_edit_skin_field_name_{skin_id}")
    keyboard.button(text="Изменить описание", callback_data=f"admin_edit_skin_field_description_{skin_id}")
    keyboard.button(text="Изменить фото", callback_data=f"admin_edit_skin_field_photo_{skin_id}")
    keyboard.button(text="Изменить шанс выпадения", callback_data=f"admin_edit_skin_field_chance_{skin_id}")
    keyboard.button(text="Удалить скин", callback_data=f"admin_delete_skin_{skin_id}")
    keyboard.button(text="Назад к списку скинов", callback_data=f"admin_edit_skin_collection_{skin.collection_id}")
    keyboard.adjust(2)
    
    await message.answer(f"Редактирование скина '{skin.name}':", reply_markup=keyboard.as_markup())
    await state.set_state(AdminStates.editing_skin)

async def edit_skin_field(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"edit_skin_field вызван с данными: {callback_query.data}")
    parts = callback_query.data.split('_')
    field = parts[4]
    skin_id = int(parts[5])
    await state.update_data(editing_skin_id=skin_id, editing_field=field)
    
    if field == "name":
        await state.set_state(AdminStates.editing_skin_name)
        await callback_query.message.edit_text("Введите новое название скина:")
    elif field == "description":
        await state.set_state(AdminStates.editing_skin_description)
        await callback_query.message.edit_text("Введите новое описание скина:")
    elif field == "photo":
        await state.set_state(AdminStates.editing_skin_photo)
        await callback_query.message.edit_text("Введите новое имя файла фото скина:")
    elif field == "chance":
        await state.set_state(AdminStates.editing_skin_chance)
        await callback_query.message.edit_text("Введите новый шанс выпадения скина (например, B - 80%):")
    
    await callback_query.answer()

async def save_edited_skin(message: types.Message, state: FSMContext):
    data = await state.get_data()
    skin_id = data['editing_skin_id']
    field = data['editing_field']
    
    skin = await Skin.get(item_id=skin_id)
    
    if field == "name":
        skin.name = message.text
    elif field == "description":
        skin.description = message.text
    elif field == "photo":
        skin.photo = message.text
    elif field == "chance":
        skin.chance = message.text
    
    await skin.save()
    await message.answer(f"Скин успешно обновлен!")
    
    # Возвращаемся в меню редактирования скина
    await show_edit_skin_menu(message, state, skin_id)

async def delete_skin(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"delete_skin вызван с данными: {callback_query.data}")
    skin_id = int(callback_query.data.split('_')[3])
    skin = await Skin.get(item_id=skin_id)
    collection_id = skin.collection_id
    
    # Удаляем скин
    await skin.delete()
    
    await callback_query.answer("Скин успешно удален!")
    
    # Возвращаемся к списку коллекций
    await show_collections_for_edit(callback_query, state)

async def admin_menu_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await admin_menu(callback_query.message, state)
    await callback_query.answer()

def register_handlers_admin(dp: Dispatcher):
    dp.message.register(admin_handler, Command('admin'), AdminFilter())
    dp.message.register(add_item_handler, Command('hack'), AdminFilter())
    dp.message.register(admin_menu, Command('admin_menu'), AdminFilter())
    
    
    dp.callback_query.register(show_collections_for_edit, F.data == "admin_edit_collections")
    dp.callback_query.register(edit_collection, F.data.startswith("admin_collection_edit_"))
    dp.callback_query.register(edit_collection_field, F.data.startswith("admin_collection_field_edit_"))
    dp.callback_query.register(delete_collection, F.data.startswith("admin_collection_delete_"))
    
    dp.message.register(save_edited_collection, AdminStates.editing_collection_name)
    dp.message.register(save_edited_collection, AdminStates.editing_collection_type)
    dp.message.register(save_edited_collection, AdminStates.editing_collection_description)
    dp.message.register(save_edited_collection, AdminStates.editing_collection_price)
    dp.message.register(save_edited_collection, AdminStates.editing_collection_active_from)
    dp.message.register(save_edited_collection, AdminStates.editing_collection_active_to)
    
    dp.callback_query.register(delete_skin, F.data.startswith("admin_delete_skin_"))
    dp.callback_query.register(show_collections_for_skin_edit, F.data == "admin_edit_skin")
    dp.callback_query.register(edit_skin_collection, F.data.startswith("admin_edit_skin_collection_"))
    dp.callback_query.register(edit_skin, F.data.startswith("admin_edit_skin_") & ~F.data.startswith("admin_edit_skin_field_"))
    dp.callback_query.register(edit_skin_field, F.data.startswith("admin_edit_skin_field_"))
    
    dp.callback_query.register(admin_menu_callback, F.data == "admin_menu_back")
    dp.callback_query.register(process_callback, AdminStates.choosing_action)
    

    dp.message.register(save_edited_skin, AdminStates.editing_skin_name)
    dp.message.register(save_edited_skin, AdminStates.editing_skin_description)
    dp.message.register(save_edited_skin, AdminStates.editing_skin_photo)
    dp.message.register(save_edited_skin, AdminStates.editing_skin_chance)
    
    dp.callback_query.register(choose_collection_for_skin, F.data.startswith("admin_collection_"))
    
    dp.message.register(add_collection, AdminStates.adding_collection)
    dp.message.register(add_collection_type, AdminStates.adding_collection_type)
    dp.message.register(add_collection_description, AdminStates.adding_collection_description)
    dp.message.register(add_collection_price, AdminStates.adding_collection_price)
    dp.message.register(finish_adding_collection, AdminStates.adding_collection_folder)
    
    dp.message.register(add_skin_name, AdminStates.adding_skin_name)
    dp.message.register(add_skin_description, AdminStates.adding_skin_description)
    dp.message.register(add_skin_photo, AdminStates.adding_skin_photo)
    dp.message.register(finish_adding_skin, AdminStates.adding_skin_chance)
    
