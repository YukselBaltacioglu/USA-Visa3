import React, { useState } from 'react';

const EmailManager = () => {
    const [emails, setEmails] = useState(['']); // İlk başta tek bir input
    const [isSubmitted, setIsSubmitted] = useState(false);  // Onay ekranı için state ekliyoruz

    // Yeni bir email input alanı ekleme
    const addEmailField = () => {
        setEmails([...emails, '']);
    };

    // Var olan bir email inputunu güncelleme
    const updateEmail = (index, value) => {
        const newEmails = [...emails];
        newEmails[index] = value;
        setEmails(newEmails);
    };

    // Bir email inputunu kaldırma
    const removeEmailField = (index) => {
        const newEmails = [...emails];
        newEmails.splice(index, 1); // İlgili index'teki emaili kaldır
        setEmails(newEmails);
    };

    // Backend'e email'leri gönderme
    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitted(true);  // Butona basıldığı anda onay ekranını gösterecek
        const response = await fetch('http://127.0.0.1:5000/emails', {  // Backend URL'i
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ emails }),  // Email'leri backend'e gönderiyoruz
        });

        const data = await response.json();
        if (response.ok) {
            console.log('Emails sent successfully:', data);
        } else {
            console.error('Failed to send emails:', data);
        }
    };

    // Eğer mailler başarılı bir şekilde gönderildiyse onay ekranı gösterelim
    if (isSubmitted) {
        return (
            <div>
                <h2>Mailler Başarıyla Gönderildi</h2>
                <p>İşleminiz başlatıldı. Lütfen bekleyin.</p>
            </div>
        );
    }

    // Normal email input formu
    return (
        <div>
            <h2>Email Manager</h2>
            <form onSubmit={handleSubmit}>
                {emails.map((email, index) => (
                    <div key={index}>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => updateEmail(index, e.target.value)}
                            required
                        />
                        <button type="button" onClick={() => removeEmailField(index)}>-</button>
                    </div>
                ))}
                <button type="button" onClick={addEmailField}>Add Email</button>
                <button type="submit">Submit Emails</button>
            </form>
        </div>
    );
};

export default EmailManager;
