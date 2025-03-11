document.addEventListener('DOMContentLoaded', async () => {
    const API_URL = "http://localhost:8000";
    const token = localStorage.getItem('token');

    if (!token) {
        alert('Please login to access the admin dashboard');
        window.location.href = 'index.html';
        return;
    }

    const logoutButton = document.getElementById('logout-button');
    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = 'index.html';
    });

    const userTableBody = document.getElementById('user-table').querySelector('tbody');
    const fileTableBody = document.getElementById('file-table').querySelector('tbody');

    try {
        const userResponse = await fetch(`${API_URL}/users/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (userResponse.ok) {
            const data = await userResponse.json();
            const users = data.users;
            users.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.username}</td>
                    <td>${user.role}</td>
                    <td>
                        <button class="action-button" onclick="changeRole('${user.username}')">Change Role</button>
                        <button class="action-button" onclick="deleteUser('${user.username}')">Delete</button>
                    </td>
                `;
                userTableBody.appendChild(row);
            });
        } else {
            alert('Failed to load users');
        }

        const fileResponse = await fetch(`${API_URL}/files/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (fileResponse.ok) {
            const data = await fileResponse.json();
            const files = data.files;
            files.forEach(file => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${file.filename}</td>
                    <td>${file.owner}</td>
                    <td>
                        <button class="action-button" onclick="deleteFile('${file.filename}', '${file.owner}')">Delete</button>
                    </td>
                `;
                fileTableBody.appendChild(row);
            });
        } else {
            alert('Failed to load files');
        }
    } catch (error) {
        console.error('Failed to load data:', error);
        alert('Failed to load data');
    }
});

async function changeRole(username) {
    const newRole = prompt('Enter new role for ' + username + ' (admin/user):', 'user');
    if (!newRole || (newRole !== 'admin' && newRole !== 'user')) {
        alert('Invalid role. Please enter either "admin" or "user".');
        return;
    }
    console.log('New role:', newRole);

    const token = localStorage.getItem('token');
    const API_URL = "http://localhost:8000";

    try {
        const response = await fetch(`${API_URL}/users/${username}/role`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({username: username, new_role: newRole })
        });

        if (response.ok) {
            alert('Role updated successfully');
            window.location.reload();
        } else {
            alert('Failed to update role');
        }
    } catch (error) {
        console.error('Failed to update role:', error);
        alert('Failed to update role');
    }
}

async function deleteUser(username) {
    if (!confirm(`Are you sure you want to delete ${username}?`)) {
        return;
    }
    const token = localStorage.getItem('token');
    const API_URL = "http://localhost:8000";

    try {
        const response = await fetch(`${API_URL}/users/${username}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert('User deleted successfully');
            window.location.reload();
        } else {
            alert('Failed to delete user');
        }
    } catch (error) {
        console.error('Failed to delete user:', error);
        alert('Failed to delete user');
    }
}

async function deleteFile(filename, owner) {
    if (!confirm(`Are you sure you want to delete ${filename} owned by ${owner}?`)) {
        return;
    }
    const token = localStorage.getItem('token');
    const API_URL = "http://localhost:8000";

    try {
        const response = await fetch(`${API_URL}/delete/${owner}/${filename}`, {
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