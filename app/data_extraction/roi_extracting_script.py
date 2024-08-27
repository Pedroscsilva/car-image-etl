import cv2
import pandas as pd
import dateutil.utils as dt

img = cv2.imread('app/data_extraction/diagrams/jpg_files/DA4407PE_diagram.pdf-1.jpg')
roi_df = pd.DataFrame(columns=['roi_name', 'x', 'y', 'w', 'h'])

def make_multiple_roi(df):
    win_name = 'roi_selection'
    cont = 'y'
    
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    x, y, w, h = cv2.selectROI(win_name, img)

    roi_name = input(f'ROI selected as {x, y, w, h}. Please name your ROI:\n')

    new_roi_data = {
        'roi_name': [roi_name],
        'x': [x],
        'y': [y],
        'w': [w],
        'h': [h]
    }

    new_data = pd.DataFrame(new_roi_data)
    df = pd.concat([df, new_data])

    cont = input('Saved with success. Continue? (y/n)\n')

    if cont == 'y':
        make_multiple_roi(df)

    else:
        df.to_csv(f'app/data_extraction/roi{dt.today()}.csv')
        print('ROI saved as .csv with success!')

make_multiple_roi(roi_df)