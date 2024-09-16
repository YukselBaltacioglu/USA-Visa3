import React, { useState } from 'react';

const EmailManager = () => {
    const [emails, setEmails] = useState(['']);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [completionStatus, setCompletionStatus] = useState('');

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
        newEmails.splice(index, 1);
        setEmails(newEmails);
    };

    // Backend'e email'leri gönderme
    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitted(true);
        const response = await fetch('http://127.0.0.1:9000/emails', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ emails }),
        });

        const data = await response.json();
        if (response.ok) {
            console.log('Emails sent successfully:', data);

            // Email gönderme işlemi tamamlandıktan sonra /complete endpoint'ine istek gönderme
            const completeResponse = await fetch('http://127.0.0.1:9000/complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: 'completed' }), // İşlemin tamamlandığını belirten veri
            });

            const completeData = await completeResponse.json();
            if (completeResponse.ok) {
                setCompletionStatus(completeData.message);
            } else {
                console.error('Failed to complete:', completeData);
            }
        } else {
            console.error('Failed to send emails:', data);
        }
    };

    if (completionStatus) {
        return (
            <div>
                <h2>{completionStatus}</h2>
            </div>
        );
    }
    if (isSubmitted) {
        return (
            <div>
                <h2>Email adresleri onaylandi.</h2>
                <p>Lutfen Bekleyiniz.</p>
            </div>
        );
    }
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
