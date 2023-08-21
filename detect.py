import torch, cv2, datetime
from models.experimental import attempt_load
from utils.general import non_max_suppression
import numpy as np

frame_count, pIn, pOut, last_ym, counted_people = 0, 0, 0, None, set()
nome_arq = datetime.datetime.today()
arquivor = open(str(nome_arq), 'x')

# Carregar o modelo na GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = attempt_load("yolov5s.pt", map_location=device)
model.to(device)
model.eval()

link = "output_video.avi"
#link = "2.mp4"
videocapture1 = cv2.VideoCapture(link)
ret, image = videocapture1.read()
line_position_sup = int(image.shape[0]/2) - 5
line_position_inf = int(image.shape[0]/2) + 5

#line_position_sup = 1180
#line_position_inf = 1190

while True:
    ret, imagem = videocapture1.read()
    if not ret:
        break
    
    image = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    image = image.astype(np.float32) / 255.0
    image = torch.from_numpy(image).to(device)
    image = image.permute(2, 0, 1).unsqueeze(0).float()
    with torch.no_grad():
        results = model(image)[0]
        pred = non_max_suppression(results, 0.3, 0.20, classes = 0, agnostic = True)
        #print(pred)

    for i, det in enumerate(pred):
        if len(det):
            for d in det:
                pessoa = d.tolist()
                x1, y1, x2, y2 = pessoa[0], pessoa[1], pessoa[2], pessoa[3]
                xm = int((pessoa[0]+pessoa[2])/2)
                ym = int((pessoa[1]+pessoa[3])/2)
                print(xm, ym, line_position_sup, line_position_inf)
                if last_ym is not None:
                    print('dif = ', str(abs(ym - last_ym)))
                    if last_ym < line_position_sup and ym >= line_position_sup and (abs(ym - last_ym) <= 100):
                        person_id = f'{int(x1)}_{int(y1)}_{int(x2)}_{int(y2)}'
                        if person_id not in counted_people:
                            counted_people.add(person_id)
                            pOut += 1
                            arquivor = open(str(nome_arq), 'a')
                            texte = arquivor.write(str(datetime.datetime.today()) + ' PORTA 01 SAIDA\n')
                            if xm >= 0 and xm <= image.shape[1]/4:
                                texte = arquivor.write(str(datetime.datetime.today()) + ' PORTA 01 SAIDA\n')
                            if xm > image.shape[1]/4 and xm <= image.shape[1]/2:
                                texte = arquivor.write(str(datetime.datetime.today()) + ' PORTA 02 SAIDA\n')
                            if xm > image.shape[1]/2 and xm <= 3*image.shape[1]/4:
                                texte = arquivor.write(str(datetime.datetime.today()) + ' PORTA 03 SAIDA\n')
                            if xm > 3*image.shape[1]/4 and xm <= image.shape[1]:
                                texte = arquivor.write(str(datetime.datetime.today()) + ' PORTA 04 SAIDA\n')
                            arquivor.close()
                            print('SAINDO')
                    elif last_ym >= line_position_sup and ym < line_position_sup and (abs(ym - last_ym) <= 100):
                        person_id = f'{int(x1)}_{int(y1)}_{int(x2)}_{int(y2)}'
                        if person_id not in counted_people:
                            counted_people.add(person_id)
                            pIn += 1
                            arquivor = open(str(nome_arq), 'a')
                            texte = arquivor.write(str(datetime.datetime.today()) + ' PORTA 01 ENTRADA\n')
                            if xm >= 0 and xm <= image.shape[1]/4:
                                texte = arquivor.write(str(datetime.datetime.today()) + ' PORTA 01 ENTRADA\n')
                            if xm > image.shape[1]/4 and xm <= image.shape[1]/2:
                                texte = arquivor.write(str(datetime.datetime.today()) + ' PORTA 02 ENTRADA\n')
                            if xm > image.shape[1]/2 and xm <= 3*image.shape[1]/4:
                                texte = arquivor.write(str(datetime.datetime.today()) + ' PORTA 03 ENTRADA\n')
                            if xm > 3*image.shape[1]/4 and xm <= image.shape[1]:
                                texte = arquivor.write(str(datetime.datetime.today()) + ' PORTA 04 ENTRADA\n')

                            arquivor.close()
                            print('ENTRANDO')
                last_ym = ym
                print(d.tolist())

    print('frame processado!!!')
