document.addEventListener('DOMContentLoaded', function() {

  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  load_mailbox('inbox');
});

function compose_email() {
  const emailsView = document.querySelector('#emails-view');
  const composeView = document.querySelector('#compose-view');

  if (emailsView && composeView) {
      emailsView.style.display = 'none';
      composeView.style.display = 'block';
  } else {
      console.error('Element not found');
      return;
  }

  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  document.querySelector('#compose-form').onsubmit = () => {
      const recipients = document.querySelector('#compose-recipients').value;
      const subject = document.querySelector('#compose-subject').value;
      const body = document.querySelector('#compose-body').value;

      fetch('/emails', {
          method: 'POST',
          body: JSON.stringify({
              recipients: recipients,
              subject: subject,
              body: body
          })
      })
      .then(response => response.json())
      .then(result => {
          load_mailbox('sent');
      });

      return false;
  };
}

function load_mailbox(mailbox) {
    const emailDetailView = document.querySelector('#email-detail-view');
    if (emailDetailView) {
        emailDetailView.remove();
    }

    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';

    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

    fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
        emails.forEach(email => {
            const emailElement = document.createElement('div');
            emailElement.className = 'email-item';
            emailElement.style.border = '1px solid grey';
            emailElement.style.padding = '10px';
            emailElement.style.margin = '10px 0';
            emailElement.style.cursor = 'pointer';
            emailElement.style.backgroundColor = email.read ? '#a69898' : 'white';

            emailElement.innerHTML = `
                <b>From:</b> ${email.sender}<br>
                <b>Subject:</b> ${email.subject}<br>
                <b>Timestamp:</b> ${email.timestamp}
            `;
            emailElement.addEventListener('click', () => view_email(email.id));
            document.querySelector('#emails-view').append(emailElement);
        });
    });
}

function view_email(email_id) {
    fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
        document.querySelector('#emails-view').style.display = 'none';
        document.querySelector('#compose-view').style.display = 'none';

        const existingDetailView = document.querySelector('#email-detail-view');
        if (existingDetailView) {
            existingDetailView.remove();
        }

        const emailDetailView = document.createElement('div');
        emailDetailView.id = 'email-detail-view';
        emailDetailView.style.padding = '20px';
        emailDetailView.style.margin = '0 auto';
        emailDetailView.style.border = '1px solid black';
        emailDetailView.style.borderRadius = '5px';
        emailDetailView.style.backgroundColor = 'white';
        emailDetailView.style.width = '80%';
        emailDetailView.innerHTML = `
            <h3>${email.subject}</h3>
            <p><b>From:</b> ${email.sender}</p>
            <p><b>To:</b> ${email.recipients.join(", ")}</p>
            <p><b>Timestamp:</b> ${email.timestamp}</p>
            <hr>
            <p>${email.body}</p>
            <button class="btn btn-sm btn-outline-primary" id="reply-button">Reply</button>
            <button class="btn btn-sm btn-outline-primary" id="archive-button">${email.archived ? 'Unarchive' : 'Archive'}</button>
        `;
        document.body.appendChild(emailDetailView);

        document.querySelector('#reply-button').addEventListener('click', () => reply_email(email));

        document.querySelector('#archive-button').addEventListener('click', () => archive_email(email_id, !email.archived));

        fetch(`/emails/${email_id}`, {
            method: 'PUT',
            body: JSON.stringify({
                read: true
            })
        });
    });
}

function archive_email(email_id, archive) {
    fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: archive
        })
    })
    .then(() => {
        load_mailbox('inbox');
    });
}

function reply_email(email) {
    compose_email();

    document.querySelector('#compose-recipients').value = email.sender;
    document.querySelector('#compose-subject').value = email.subject.startsWith('Re:') ? email.subject : `Re: ${email.subject}`;
    document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote:\n${email.body}\n\n`;

    window.scrollTo(0, 0);
}
