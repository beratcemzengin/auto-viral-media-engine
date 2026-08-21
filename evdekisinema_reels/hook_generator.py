import random

GENRE_HOOKS = {
    "Korku": [
        "BU GECE EVDE YALNIZSANIZ SAKIN AÇMAYIN!",
        "TÜYLERİNİZİ DİKEN DİKEN EDECEK O FİLM...",
        "IŞIKLARI KAPATIP İZLEYEBİLECEK MİSİNİZ?",
        "SON ZAMANLARIN EN KORKUNÇ BAŞYAPITI!",
        "GERİLİMDEN NEFESİNİZİ KESECEK KORKU FİLMİ"
    ],
    "Gerilim": [
        "SON SANİYESİNE KADAR TERS KÖŞE YAPAN FİLM!",
        "BEYİN YAKAN AKIL OYUNLARI DOLU BİR BAŞYAPIT",
        "NEFESİNİZİ TUTARAK İZLEYECEĞİNİZ GERİLİM!",
        "BİTTİĞİNDE DAKİKALARCA DÜŞÜNDÜRECEK FİLM",
        "HER SAHNESİ AYRI BİR ŞOK ETKİSİ YARATIYOR!"
    ],
    "Bilim-Kurgu": [
        "BEYNİNİZİ YAKACAK BİLİM KURGU BAŞYAPITI!",
        "GERÇEKLİK ALGINIZI TAMAMEN DEĞİŞTİRECEK FİLM",
        "GELECEĞİ ÖNCEDEN GÖREN EFSANEVİ BİR YAPIM",
        "UZAY VE ZAMAN KAVRAMINI UNUTTURACAK FİLM!",
        "AKIL OYUNLARI SEVENLERİN KAÇIRMAMASI GEREKEN FİLM!"
    ],
    "Aksiyon": [
        "ADRENALİN SEVİYENİZİ TAVAN YAPTIRACAK FİLM!",
        "BİR SANİYE BİLE GÖZÜNÜZÜ AYIRAMAYACAKSINIZ!",
        "İNTİKAM VE ADRENALİN DOLU EFSANE BİR YAPIM!",
        "SOLUKSUZ İZLEYECEĞİNİZ YILIN EN İYİ AKSİYONU",
        "AKSİYON SEVERLER EKRAN BAŞINA: İŞTE O FİLM!"
    ],
    "Dram": [
        "GÖZYAŞLARINIZA HAKİM OLAMAYACAĞINIZ BİR HİKAYE...",
        "KALBİNİZE DOKUNACAK GERÇEK BİR HAYAT DERSİ",
        "İZLERKEN DERİNDEN ETKİLENECEĞİNİZ BAŞYAPIT",
        "RUHUNUZA DOKUNACAK EFSANE BİR DRAM FİLMİ",
        "HERKESİN HAYATINDA EN AZ BİR KEZ İZLEMESİ GEREKEN FİLM"
    ],
    "Komedi": [
        "GÜLMEKTEN KARNINIZA AĞRILAR GİRECEK FİLM!",
        "MODUNUZU ANINDA YÜKSELTECEK HARİKA BİR KOMEDİ",
        "HAFTANIN EN EĞLENCELİ FİLM TAVSİYESİ!",
        "ARKADAŞLARINIZLA İZLEYEBİLECEĞİNİZ EN İYİ KOMEDİ"
    ]
}

DEFAULT_HOOKS = [
    "HAFTANIN EN ÇOK KONUŞULAN FİLM TAVSİYESİ!",
    "BİTTİĞİNDE ETKİSİNDEN ÇIKAMAYACAĞINIZ O FİLM...",
    "BU AKŞAM NE İZLESEM DİYENLER İÇİN HARİKA TAVSİYE!",
    "SİNEMA DÜNYASINI KASIP KAVURAN YENİ BAŞYAPIT!",
    "HERKESİN LİSTESİNE EKLEMESİ GEREKEN O FİLM!"
]

def generate_viral_hook(genres_str="", vote_average=7.0):
    for genre, hooks in GENRE_HOOKS.items():
        if genre.lower() in genres_str.lower():
            return random.choice(hooks)
    if vote_average >= 8.0:
        return f"IMDb {vote_average} PUANLI BAŞYAPIT FİLM TAVSİYESİ!"
    return random.choice(DEFAULT_HOOKS)
