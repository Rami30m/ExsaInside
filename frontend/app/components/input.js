"use client";

import { useState } from "react";

export default function Input({ onResultsUpdate }) {
    const [isLoading, setIsLoading] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file && file.type === 'text/csv') {
            setSelectedFile(file);
        } else {
            alert('Пожалуйста, выберите файл формата .csv');
        }
    };

    const handleSubmit = async () => {
        if (!selectedFile) {
            alert('Пожалуйста, выберите файл');
            return;
        }

        setIsLoading(true);
        
        try {
            const formData = new FormData();
            formData.append('file', selectedFile);

            // Замените URL на ваш реальный эндпоинт бекенда
            const response = await fetch('http://localhost:8000/analyze/', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const results = await response.json();
                console.log(results);   
                onResultsUpdate(results);
            } else {
                throw new Error('Ошибка при загрузке файла');
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при загрузке файла');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-2 text-white items-center">
                <label className="text-xl font-bold mb-3" htmlFor="file">Вставьте файл формата .csv</label>
                <input 
                    className="bg-[red] p-5 rounded-md text-center" 
                    type="file" 
                    name="file" 
                    id="file"
                    accept=".csv"
                    onChange={handleFileChange}
                />
                {selectedFile && (
                    <p className="text-sm text-gray-300">Выбран файл: {selectedFile.name}</p>
                )}
                <button
                    onClick={handleSubmit}
                    disabled={!selectedFile || isLoading}
                    className={`px-6 py-2 rounded-md font-medium ${
                        !selectedFile || isLoading
                            ? 'bg-gray-500 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700'
                    } text-white`}
                >
                    {isLoading ? 'Загрузка...' : 'Отправить файл'}
                </button>
            </div>
        </div>
    )
}