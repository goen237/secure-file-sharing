document.addEventListener('DOMContentLoaded', async () => {
    const API_URL = "http://localhost:8000";

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch(`${API_URL}/login/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('token', data.access_token);
                    localStorage.setItem('refresh_token', data.refresh_token);
                    localStorage.setItem('username', username);
                    localStorage.setItem('role', data.role);
                    if (data.role === 'admin') {
                        window.location.href = 'admin.html';
                    } else {
                        window.location.href = 'dashboard.html';
                    }
                } else {
                    const errorData = await response.json();
                    alert(errorData.detail);
                }
            } catch (error) {
                console.error('Login failed:', error);
                alert('Login failed');
            }
        });
    }

    const halloName = document.getElementById('hallo');
    if (halloName) {
        const username = localStorage.getItem('username');
        if (username) {
            halloName.innerText = `Hallo ${username}`;
        }
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('reg-username').value;
            const password = document.getElementById('reg-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            if (password !== confirmPassword) {
                alert('Passwords do not match');
                return;
            }

            try {
                const response = await fetch(`${API_URL}/register/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                if (response.ok) {
                    alert('Registration successful');
                } else {
                    alert('Registration failed');
                }
            } catch (error) {
                console.error('Registration failed:', error);
                alert('Registration failed');
            }
        });
    }

    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const file = document.getElementById('file').files[0];
            const formData = new FormData();
            formData.append('file', file);

            const token = localStorage.getItem('token');

            try {
                const response = await fetch(`${API_URL}/upload/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData
                });

                if (response.ok) {
                    alert('File uploaded successfully');
                    window.location.reload();
                } else {
                    alert('File upload failed');
                }
            } catch (error) {
                console.error('File upload failed:', error);
                alert('File upload failed');
            }
        });
    }

    const downloadForm = document.getElementById('download-form');
    if (downloadForm) {
        downloadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const filename = document.getElementById('filename').value;

            const token = localStorage.getItem('token');

            try {
                const response = await fetch(`${API_URL}/download/${filename}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                } else {
                    alert('File download failed');
                }
            } catch (error) {
                console.error('File download failed:', error);
                alert('File download failed');
            }
        });
    }

    const fileTable = document.getElementById('file-table-user');
    if (fileTable) {
        const fileTableBody = fileTable.querySelector('tbody');
        if (fileTableBody) {
        const token = localStorage.getItem('token');
        if (!token) {
            alert('Please login to view files');
            window.location.href = 'index.html';
            return;
        }

        try {
            const fileListResponse = await fetch(`${API_URL}/files/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (fileListResponse.ok) {
                const data = await fileListResponse.json();
                if (data.files.length === 0) {
                    const noFilesRow = document.createElement('tr');
                    noFilesRow.innerHTML = `
                        <td colspan="2">No files found</td>
                    `;
                    fileTableBody.appendChild(noFilesRow);
                } else {
                    data.files.forEach(file => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${file}</td>
                            <td>
                                <button class="action-button" onclick="prev_file('${file.filename}')">Preview</button>
                                <button class="action-button" onclick="deletefile('${file.filename}')">Delete</button>
                            </td>
                        `;
                        fileTableBody.appendChild(row);
                    });
                }
            } else {
                alert('Failed to load files');
            }
        } catch (error) {
            console.error('Failed to load files:', error);
            alert('Failed to load files');
        }
    }

    const logout = document.getElementById('logout-button');
    if (logout) {
        logout.addEventListener('click', () => {
            localStorage.removeItem('token');
            localStorage.removeItem('refresh_token');
            window.location.href = 'index.html';
        });
    }

    const password_to_profile = document.getElementById('change-password-button');
    if (password_to_profile) {
        password_to_profile.addEventListener('click', () => {
            window.location.href = 'profile.html';
        }
        );
    }

    const change_pwd = document.getElementById('change-password-form');
    if (change_pwd) {
        change_pwd.addEventListener('submit', async (e) => {
            e.preventDefault();
            const access_token = localStorage.getItem('token');
            if (!access_token) {
                window.location.href = 'index.html';
                return;
            }
            const currentPassword = document.getElementById('current-password').value;
            const password = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-new-password').value;

            if (password !== confirmPassword) {
                alert('Passwords do not match');
                return;
            }

            try {
                const response = await fetch(`${API_URL}/change-password/`, {
                    method: 'PUT',
                    headers: {
                        "Authorization": `Bearer ${access_token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ current_password: currentPassword, new_password: password })
                });

                if (response.ok) {
                    alert('Password changed successfully');
                    window.location.href = 'dashboard.html';
                } else {
                    alert('Password change failed');
                }
            } catch (error) {
                console.error('Password change failed:', error);
                alert('Password change failed');
            }
        });
    }

    // alle 28 Minuten wird automatisch ein neuer Token geholt
    if (localStorage.getItem('refresh_token')) {
        setInterval(async () => {
            const refresh_token = localStorage.getItem('refresh_token');
            if (refresh_token) {
                try {
                    const response = await fetch(`${API_URL}/refresh/`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${refresh_token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ refresh_token })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        localStorage.setItem('token', data.access_token);
                    } else {
                        alert('Failed to refresh token');
                    }
                } catch (error) {
                    console.error('Failed to refresh token:', error);
                    alert('Failed to refresh token');
                }
            }
        }, 14 * 60 * 1000);

    }
    }
    // }, 28 * 60 * 1000);
});


async function deletefile(filename) {
    if (!confirm(`Are you sure you want to delete ${filename}?`)) {
        return;
    }
    const token = localStorage.getItem('token');
    const API_URL = "http://localhost:8000";

    try {
        const response = await fetch(`${API_URL}/delete/${filename}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert('File deleted successfully');
            window.location.reload();
        } else {
            alert('Failed to delete file');
        }
    } catch (error) {
        console.error('Failed to delete file:', error);
        alert('Failed to delete file');
    }
}

async function prev_file(filename) {
    const token = localStorage.getItem('token');
    const API_URL = "http://localhost:8000";

    try {
        const response = await fetch(`${API_URL}/preview/${filename}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            window.open(url, '_blank');
        } else {
            alert('File preview failed');
        }
    } catch (error) {
        console.error('File preview failed:', error);
        alert('File preview failed');
    }
}