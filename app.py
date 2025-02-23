from flask import Flask, render_template, request, session, redirect, url_for
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)
app.secret_key = 'une_cle_secrete_tres_longue'

SENDGRID_API_KEY = 'VOTRE_CLE_API_SENDGRID'
FROM_EMAIL = 'votre_email@exemple.com'
ADMIN_EMAIL = 'admin@exemple.com'

produits = {
    1: {'nom': 'Produit A', 'prix': 20, 'image': 'produit_a.jpg'},
    2: {'nom': 'Produit B', 'prix': 30, 'image': 'produit_b.jpg'},
    # Ajoutez d'autres produits
}

@app.route('/')
def index():
    return render_template('index.html', produits=produits)

@app.route('/panier', methods=['GET', 'POST'])
def panier():
    if 'panier' not in session:
        session['panier'] = {}

    if request.method == 'POST':
        produit_id = int(request.form['produit_id'])
        quantite = int(request.form['quantite'])
        session['panier'][produit_id] = quantite
        session.modified = True
        return redirect(url_for('panier'))

    panier_details = []
    total = 0
    for produit_id, quantite in session['panier'].items():
        produit = produits[produit_id]
        prix_total_produit = produit['prix'] * quantite
        panier_details.append({
            'produit': produit,
            'quantite': quantite,
            'prix_total': prix_total_produit
        })
        total += prix_total_produit

    return render_template('panier.html', panier=panier_details, total=total)

@app.route('/commande', methods=['POST'])
def commande():
    if 'panier' not in session or not session['panier']:
        return redirect(url_for('index'))

    message_client = Mail(
        from_email=FROM_EMAIL,
        to_emails=request.form['email'],
        subject='Confirmation de commande',
        html_content=construire_contenu_email(session['panier'], produits)
    )
    message_admin = Mail(
        from_email=FROM_EMAIL,
        to_emails=ADMIN_EMAIL,
        subject='Nouvelle commande',
        html_content=construire_contenu_email(session['panier'], produits)
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response_client = sg.send(message_client)
        response_admin = sg.send(message_admin)
        print(response_client.status_code)
        print(response_admin.status_code)
    except Exception as e:
        print(e)

    session['panier'] = {}
    session.modified = True
    return render_template('confirmation.html')

def construire_contenu_email(panier, produits):
    contenu = '<h1>Détails de la commande</h1><ul>'
    for produit_id, quantite in panier.items():
        produit = produits[produit_id]
        contenu += f'<li>{produit["nom"]} x {quantite}</li>'
    contenu += '</ul>'
    return contenu

if __name__ == '__main__':
    app.run(debug=True)
