import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

# Crear el modelo
def crear_modelo(input_shape):
    modelo = Sequential([
        Dense(256, activation='relu', input_shape=input_shape),
        Dropout(0.3),
        Dense(256, activation='relu'),
        Dropout(0.3),
        Dense(128, activation='relu'),
        Dropout(0.3),
        Dense(88, activation='softmax')  # 88 teclas de piano
    ])
    modelo.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return modelo

# Entrenar el modelo
modelo = crear_modelo((X.shape[1],))
modelo.fit(X, y_labels, epochs=50, batch_size=32, validation_split=0.2)
