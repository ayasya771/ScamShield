"""
Curated training data for ScamShield.

Each message is a short SMS-style text. The collection is deliberately
*balanced* (roughly equal scam / legitimate) and contains tricky examples on
purpose:

  * legitimate messages that DO contain links, money amounts or verification
    codes (real banks, couriers and 2FA messages look like this), and
  * scam messages that contain NONE of those obvious signals (the "hi mum,
    new number" trick, gift-card-for-the-boss fraud, phone-call scams).

The point is to force the model to learn realistic word patterns rather than a
single give-away keyword such as "http". The messages are hand-written
archetypes inspired by publicly reported smishing campaigns; they contain no
real personal data.
"""

# --------------------------------------------------------------------------- #
#  Scam / smishing messages                                                   #
# --------------------------------------------------------------------------- #
SCAM = [
    # --- fake parcel / delivery -------------------------------------------- #
    "Royal Mail: Your parcel has a £2.99 shipping fee pending. Pay now to avoid return: http://royalmail-redelivery.info",
    "USPS: We could not deliver your package due to an incomplete address. Update here: https://usps-track.cc/verify",
    "DHL: Your shipment is on hold at customs. Pay the £1.45 fee to release it: dhl-customs-pay.top/uk",
    "FedEx alert: package FX9120 is pending delivery. Confirm your details: http://fedex-confirm.click",
    "Your Hermes parcel could not be delivered. Reschedule for £1.99: hermes-reschedule.info",
    "Evri: a redelivery fee of £1.50 is required for your parcel. Pay at evri-pay.xyz to receive it today",
    "Amazon Logistics: your delivery failed. Verify your address within 24h or it will be returned: amzn-redeliver.top",
    "An Post: your item is awaiting a €3.00 customs charge. Settle now: anpost-customs.click/pay",
    "Your parcel from SHEIN is held. Pay the £1.99 release fee: shein-delivery.cc/pay",
    "We tried to deliver your package but no one was home. Pay redelivery: parcel-redeliver.top/uk",
    "Royal Mail: a parcel is awaiting collection. A £1.99 fee applies: royalmail-collect.click/uk",
    "Your delivery is scheduled but your address is incomplete. Fix it now: delivery-fix.click/uk",
    "You have an unclaimed package waiting. Confirm your identity to release it: pkg-release.top",

    # --- fake bank / payment ----------------------------------------------- #
    "HSBC: We detected an unusual login to your account. Verify your identity now: hsbc-secure-login.com",
    "Your Barclays account has been suspended. Restore access immediately: http://barclays-verify.info",
    "Lloyds Bank: A new payee was added to your account. If this wasn't you, cancel here: lloyds-cancel.top",
    "NatWest: We blocked a payment of £820 to AMAZON. Was this you? Confirm: natwest-fraud.cc/check",
    "Santander Alert: your card has been locked for security. Reactivate now: santander-reactivate.click",
    "Your bank account access is temporarily limited. Re-verify your details to continue: secure-bank-uk.top",
    "Monzo: suspicious activity detected. Approve or freeze the £499 payment here: monzo-app-secure.info",
    "We have suspended your online banking. Click to confirm your card and PIN: ukbank-confirm.xyz",
    "Your card ending 8821 has been temporarily blocked. Call 0800 555 0133 to verify your identity",
    "Bank security: reply with your full card number and expiry to confirm you are the account holder",
    "Bank fraud team: confirm the 6-digit code we texted you so we can stop the thief",
    "You have 1 new secure message from your bank. Sign in to read it: secure-message-bank.cc",
    "Your National Insurance number has been suspended due to suspicious activity. Call 0300 555 0123 now",

    # --- prize / lottery --------------------------------------------------- #
    "Congratulations! You have won a £1,000 Tesco gift card. Claim within 24 hours: tesco-rewards.top/win",
    "You are today's lucky winner of a brand new iPhone 15 Pro! Claim here: apple-giveaway.click",
    "WINNER! Your mobile number was selected in our £500,000 prize draw. Reply CLAIM to proceed",
    "Your number has won the National Lottery bonus. Send your bank details to receive £85,000",
    "FREE £100 ASDA voucher just for you! Limited stock, claim now: asda-vouchers.info",
    "You've been chosen to receive a £750 Amazon reward. Verify to claim: amazon-rewards-uk.top",
    "Win a £200 Greggs voucher! Just complete this short survey: greggs-survey-rewards.click",
    "Your number has been entered into a £10,000 cash draw. Confirm to enter: cash-draw-uk.top",
    "Congratulations! Your email was randomly selected for a $950,000 grant from the UN. Reply to claim",

    # --- tax / government -------------------------------------------------- #
    "HMRC: You are due a tax refund of £284.50. Claim before the deadline: hmrc-refund-gov.click",
    "GOV.UK: You have an outstanding tax payment. Avoid legal action by paying now: gov-uk-tax.top",
    "IRS Final Notice: pay your overdue balance immediately to avoid an arrest warrant. Call 1-800-555-0199",
    "DVLA: Your vehicle tax payment failed. Update your details to avoid a £1,000 fine: dvla-vehicle-tax.cc",
    "You have an unpaid road toll of £4.20. Pay now to avoid a penalty charge: toll-pay-uk.click",
    "Ofgem energy rebate: you are entitled to a £400 refund. Claim now: ofgem-rebate.top/apply",
    "Inland Revenue: you owe £612 in unpaid tax. Settle immediately to avoid prosecution: tax-settle.click",
    "You qualify for a £3,500 government grant. No repayment needed. Apply: gov-grant-uk.top",
    "You missed a court date. Pay the fine immediately to avoid arrest: court-fines-pay.cc",

    # --- tech support / subscription --------------------------------------- #
    "Norton: Your subscription has auto-renewed for $399.99. To cancel, call 1-888-555-0142",
    "Geek Squad: Your plan renews today for £349.99. Dispute this charge: call 0203 555 0117",
    "McAfee renewal confirmed: $299. If you did not authorise this, call support immediately",
    "Microsoft Security: Your computer is infected with a virus. Call 0800 555 0188 now to fix it",
    "Your Apple iCloud storage is full and your account will be deleted. Verify: apple-icloud-verify.top",
    "PayPal: Your account has been limited. Resolve the issue to avoid suspension: paypal-resolve.click",
    "Your Audible subscription will renew at £79.99. To cancel call 0203 555 0190 now",
    "We detected malware on your device. Download our security tool immediately: secure-device.top/scan",
    "Hello, this is Amazon security. Press 1 now to speak to an agent about suspicious activity on your account",

    # --- streaming / account ----------------------------------------------- #
    "Netflix: Your payment was declined. Update your billing details to keep watching: netflix-billing.top",
    "Disney+: we couldn't process your renewal. Re-enter your card here: disneyplus-update.cc",
    "Spotify Premium: your payment failed. Update now to avoid losing access: spotify-pay.click",
    "Your Apple ID has been locked due to suspicious activity. Unlock now: appleid-unlock.info",
    "Your Facebook account violated our terms and will be disabled. Appeal here: fb-appeal-center.top",
    "Instagram: your account has been reported for copyright. Verify to avoid deletion: ig-verify.cc",
    "WhatsApp: your account will expire today. Renew your subscription for £0.99: whatsapp-renew.top",
    "Your Steam account has been flagged. Verify ownership to avoid a ban: steam-verify.cc",
    "Your Coinbase account has a pending withdrawal of 0.4 BTC. Cancel it here: coinbase-secure.click",

    # --- family / authority impersonation ---------------------------------- #
    "Hi mum, I dropped my phone down the toilet and this is my new number. Can you message me on WhatsApp?",
    "Dad it's me, my phone is broken so I'm texting from a friend's. I need help paying a bill, can you transfer?",
    "Hey it's your daughter, new number! I'm locked out of my bank, can you send £250 just for today?",
    "Urgent from your boss: I'm in a meeting, buy 4 Amazon gift cards of £100 each and send me the codes ASAP",

    # --- job / money-making scams ------------------------------------------ #
    "We reviewed your CV. Earn £450/day working from home, just 2 hours. Reply YES to start",
    "Congratulations, you're hired! Send your bank details and a £50 onboarding fee to begin payroll",
    "Amazon is hiring remote reviewers, $35 per task. Start today: amazon-jobs-apply.top",
    "Part-time job: get paid daily to like videos. Join our team on WhatsApp: +44 7700 900123",
    "Get rich quick! Turn £100 into £5,000 in 7 days with our trading bot. Sign up: profit-bot.top",
    "Get a £5,000 loan approved instantly, no credit check. Apply now: instant-loan-uk.top",

    # --- crypto / investment ----------------------------------------------- #
    "Bitcoin alert: invest £250 today and earn £3,000 in a week. Guaranteed. Join: crypto-profit.top",
    "Your crypto wallet requires verification or your funds will be frozen: wallet-verify.click",
    "Elon Musk is giving away free Bitcoin! Send 0.1 BTC and receive 0.5 BTC back. Limited time only",

    # --- 2FA / verification phishing --------------------------------------- #
    "Your verification code is 884213. To stop this login, share the code with our agent on 0800 555 0166",
    "Someone is trying to access your account. Reply with the 6-digit code we just sent to block them",

    # --- romance / advance-fee --------------------------------------------- #
    "Hi, I came across your profile and I think you're amazing. Let's chat on Telegram: love_match88",
    "I am a US soldier overseas and need help transferring my savings. Can I trust you with my heart?",
    "Hello dear, I am a widow with £2.5m to donate to a kind person. Reply to receive your share",

    # --- utilities / refunds / misc ---------------------------------------- #
    "Your electricity bill is overdue. Service will be cut today unless you pay: energy-pay-now.top",
    "EE: your bill payment failed. Update your card to avoid disconnection: ee-billing-update.cc",
    "Your TV Licence is about to expire. Renew now to avoid a £1,000 fine: tvlicence-renew.click",
    "You have been overcharged by your energy supplier. Claim your £298 refund: energy-refund.top",
    "Claim your COVID compensation of £750 today. Limited time: covid-claim-uk.top",
    "We owe you a £180 water bill refund. Provide your account details to claim: water-refund.top",
    "Your Three mobile bill is overdue. Pay £18.50 now to avoid disconnection: three-pay.top",
    "Your TalkTalk account is due a £90 loyalty reward. Claim before midnight: talktalk-rewards.top",
    "Your O2 reward is ready! Claim 100GB free data now: o2-rewards.click",
    "Vodafone: you have unused reward points worth £50. Redeem before they expire: vodafone-points.top",
    "Your meter reading is overdue and a fine applies. Submit now: meter-submit.top/uk",

    # --- account / urgency / closing variety ------------------------------- #
    "Final reminder: your account will be permanently closed in 24 hours. Verify now to keep it active",
    "Security Alert: we noticed a sign-in from a new device in Russia. Secure your account: secure-now.top",
    "You have (1) undelivered voicemail. Listen here: voicemail-portal.click",
    "Action required: confirm your details or your Amazon Prime membership will be cancelled today",
    "ALERT: Your Google account password was changed. If this wasn't you, recover it: google-recovery.cc",
    "Your Amazon account has been put on hold. Verify your payment method to restore access: amzn-verify.top",
    "Your subscription to Audible will renew at £79.99 unless you cancel: audible-cancel.top",
    "Costco: you've been selected for a $500 reward for your loyalty. Claim here: costco-reward.click",
    "Your Argos order A8841 could not be processed. Update payment: argos-pay.top",
    "Important: your pension is at risk. Speak to an advisor today to protect your savings. Call now",
    "Free Wi-Fi: log in with your bank details to access unlimited internet for life",
    "Your iPhone has been located after being lost. Sign in to view its location: find-iphone-locate.top",
    "Your account has unusual sign-in activity. Verify within 12 hours or it will be suspended: verify-account.top",
    "You've got a refund of £129.99 waiting. Confirm your card to receive it: refund-claim.top",
    "PayPal: You sent £450 to John Carter. If you didn't authorise this, cancel here: paypal-cancel.top",
    "Your Amazon Prime will renew for £95 today. Stop the charge: amazon-stop-renewal.cc",
    "Security notice: 3 failed login attempts on your account. Lock or verify now: account-secure.top",
    "Apple Pay: a payment of £610 is pending approval. Review now: applepay-review.cc",
    "Your eBay item sold! Buyer paid via PayPal. Confirm shipping to release funds: ebay-confirm.top",
    "Urgent: your child's school fees are overdue. Pay today to avoid removal: schoolpay-now.click",
    "Your warranty is about to expire. Renew your car's cover now to stay protected. Call 0800 555 0150",
    "Final notice: your domain will be suspended. Renew now to keep your website online: domain-renew.top",
    "Reactivate your suspended PayPal account in 24 hours or lose access permanently: paypal-reactivate.click",
    "Amazon: unusual purchase of £799 detected. Cancel the order now: amazon-cancel-order.top",
    "You've received a payment request of £230 from an unknown sender. Decline here: payment-decline.cc",
    "Last chance: claim your £1,200 holiday voucher before it expires tonight: holiday-claim.click",
    "Your Uber account shows a £45 unpaid trip. Settle now to avoid suspension: uber-billing.top",
    "DVSA: Your driving licence needs to be updated to remain valid. Update now: dvla-update.click",
]

# --------------------------------------------------------------------------- #
#  Legitimate messages                                                        #
# --------------------------------------------------------------------------- #
LEGIT = [
    # --- everyday personal ------------------------------------------------- #
    "Hey, are we still on for dinner tonight at 7?",
    "Can you grab some milk on the way home please?",
    "Happy birthday!! Hope you have an amazing day xx",
    "Running about 10 minutes late, so sorry! See you soon",
    "Did you get home okay last night?",
    "Mum, I'll be at yours around 6 for dinner. Need me to bring anything?",
    "Thanks so much for today, I had a lovely time :)",
    "Don't forget we have the dentist tomorrow at 9am",
    "Call me when you're free, no rush",
    "I left my charger at yours, could you bring it Saturday?",
    "Good luck with your interview today, you've got this!",
    "The kids are asking when you'll be back, drive safe",
    "Just landed, will text you when I'm at the hotel",
    "Are you coming to football on Sunday?",
    "Let's catch up this weekend, it's been ages",
    "Hey, can you send me that recipe you made last week? It was delicious",
    "I'll pick the kids up from school today, you have your meeting",
    "Sorry I missed your call, I was on the train. Call you back in 10",
    "Quick one, what time does the party start on Saturday?",
    "Just checking you got home safe, let me know x",
    "Can we move our coffee to 11 instead of 10? Something came up",
    "Looking forward to seeing you both at the weekend!",
    "The plumber is coming between 9 and 12 tomorrow, can you be in?",
    "I've booked the holiday! Flights are on the 14th, so excited",
    "Don't forget bin day is tomorrow morning",
    "I'm at the station, where shall I meet you?",
    "Thanks for lunch today, my treat next time!",
    "Can you water the plants while we're away? Spare key is under the mat",
    "Morning! Coffee before work? I'm buying",
    "Happy anniversary! Can't believe it's been 5 years already",
    "I'm so proud of you for finishing the marathon today!",
    "Let me know when you're leaving and I'll put the kettle on",
    "Could you feed the cat tonight? I'll be back late",
    "Great news, I got the job! Drinks to celebrate this weekend?",
    "The weather looks good for Saturday, beach day?",
    "Reminder: book club is at mine on Wednesday, 7:30",
    "Can you forward me Grandma's address? I'm sending her a card",
    "I've left dinner in the oven, just heat it for 20 mins",
    "See you at the gym at 6? Leg day today",
    "Thanks for helping me move, I owe you big time",
    "Did you watch the match last night? What a goal!",

    # --- work / school ----------------------------------------------------- #
    "The 3pm meeting has been moved to room 4B",
    "Reminder: please submit your timesheet by Friday",
    "Can you send me the slides before the call? Thanks",
    "Great work on the report today, the client loved it",
    "I'm working from home tomorrow, ping me on Teams if you need me",
    "The office will be closed on Monday for the bank holiday",
    "Your shift on Thursday has been confirmed, 9am to 5pm",
    "Please remember to book your annual leave by the end of the month",
    "Parents evening is on Thursday from 4pm. Sign up for a slot via the school app",
    "School closed tomorrow due to staff training. Sorry for the short notice",
    "Your child was a superstar in class today, well done to them!",
    "Reminder: PE kit needed tomorrow",
    "The team lunch is booked for Friday at 1pm, hope you can make it",
    "Welcome to the team! Your first day is Monday, we'll meet you in reception at 9",

    # --- appointments / health (legit) ------------------------------------- #
    "Reminder: you have a GP appointment with Dr Patel on Tue 10 June at 2:30pm. Reply C to confirm",
    "Your dental check-up is booked for Thursday at 11am. Please arrive 5 minutes early",
    "Your car is booked in for its MOT on 12 June. We'll call if anything needs attention",
    "This is a reminder of your hair appointment tomorrow at 4pm. See you then!",
    "Your prescription is ready to collect from the pharmacy",
    "Your physio session is confirmed for Friday at 1pm",
    "Your blood test results are ready. Please book a call with your GP to discuss",
    "Your flu jab appointment is booked for Saturday at 10:15 at the pharmacy",
    "Your appointment is tomorrow. Reply C to confirm or R to reschedule",

    # --- delivery (legit, real domains / no payment ask) ------------------- #
    "Your Amazon order has shipped and will arrive tomorrow. Track it in the app",
    "DPD: Your parcel will be delivered today between 2pm and 3pm. Track at dpd.co.uk",
    "Royal Mail: Sorry we missed you. Your parcel is at your local delivery office for collection",
    "Your ASOS order is out for delivery and will arrive today",
    "Ocado: Your delivery is on its way and will arrive within the hour",
    "Your Just Eat order from Pizza Express has been picked up and is on its way",
    "Argos: Your order is ready to collect from the Oxford Street store",
    "Your package was left with your neighbour at number 12",
    "Your Deliveroo order has been delivered. Enjoy your meal!",
    "Your delivery driver is 3 stops away",
    "Your parcel has been delivered and signed for",

    # --- bank / finance (legit alerts, no scare link) ---------------------- #
    "A payment of £42.10 to TESCO STORES was made on your debit card ending 4471",
    "Your monthly statement is now ready to view in the app",
    "You've set up a new standing order of £150 to SAVINGS. No action needed",
    "Your salary of £2,140.00 has been paid into your account",
    "Your credit card payment of £75 was received. Thank you",
    "Low balance alert: your current account balance is £18.43",
    "Your direct debit to NETFLIX of £10.99 will be taken on the 3rd",
    "Your new debit card has been posted and should arrive within 5 working days",
    "Your savings goal 'Holiday' has reached £1,000. Well done!",
    "Interest of £4.21 has been added to your savings account",
    "Your order has been refunded. The amount will appear in 3 to 5 working days",

    # --- 2FA / sign-in (legit, never-share wording) ------------------------ #
    "Your verification code is 558190. Do not share this code with anyone",
    "558102 is your one-time passcode. We will never ask you to share it",
    "Your login code is 730014. If you didn't request this, you can ignore this message",
    "Your Microsoft account security code is 4471. If this wasn't you, ignore this message",
    "Use code 901882 to complete your sign-in. Never share this code with anyone, including staff",
    "Your PayPal security code is 220194. Don't share it with anyone",

    # --- brand promo (legit, STOP / unsubscribe) --------------------------- #
    "20% off everything this weekend at GAP. Reply STOP to opt out",
    "Your Nando's loyalty card has a free starter waiting. Reply STOP to unsubscribe",
    "Costa: Enjoy a free cake with any drink this week. Show this text in store. Txt STOP to opt out",
    "New season has landed at Zara. Shop now. Reply STOP to unsubscribe",
    "Domino's: 2 for Tuesday is back! Order online. Text STOP to opt out",

    # --- utilities / official (legit, manage in app) ----------------------- #
    "Your EE bill of £29.00 is ready. Manage it anytime in the My EE app",
    "Thames Water: your next payment of £38 is due on 15 June. Manage your account at thameswater.co.uk",
    "Your British Gas statement is ready to view in your online account",
    "Your council tax direct debit of £142 will be taken on 1 July",
    "Your library books are due back on 18 June. Renew online if you need longer",

    # --- bookings / confirmations (legit) ---------------------------------- #
    "Your table for 2 at 7:30pm tonight is confirmed. See you soon!",
    "Thanks for your order! It will be ready for collection at 5pm",
    "Your booking reference is BR8821. Show this at check-in",
    "Your train ticket is booked. Coach C, seat 24. Have a good journey",
    "Your cinema tickets are confirmed for Saturday 8pm, screen 3",
    "Your appointment with the optician is confirmed for Monday at 3pm",
    "Your gym membership has been renewed. Enjoy your workouts!",
    "Your Uber is arriving now. Look for a blue Toyota, reg LK19 ABC",
    "Your Trainline ticket for the 08:15 to London is ready in the app",
    "Your flight BA294 is on time. Boarding at gate 12 from 14:30",
    "Your hotel booking at the Premier Inn is confirmed for 2 nights",
    "Your table booking has been updated to 8pm as requested",
    "Your subscription renews next week. No action needed, just a heads up",
    "Your MOT is due next month. Book online or call the garage to arrange",

    # --- legit with a link to a genuine brand domain ----------------------- #
    "Your John Lewis order is confirmed. View your receipt at johnlewis.com/orders",
    "Track your Apple order anytime at apple.com using your order number",
    "Your NHS appointment details are available in your account at nhs.uk",
    "Manage your booking at britishairways.com with your reference",
]


def load():
    """Return the full dataset as a list of (text, label) pairs."""
    data = [(text, "scam") for text in SCAM]
    data += [(text, "legit") for text in LEGIT]
    return data


if __name__ == "__main__":
    data = load()
    n_scam = sum(1 for _, label in data if label == "scam")
    n_legit = len(data) - n_scam
    print(f"{len(data)} messages: {n_scam} scam, {n_legit} legit")
