from pingtool import *
from tkinter import *
import pygame

'''
    GUI done by Jawad Srour
'''

root = Tk()

root.title("The Pinger")

root.geometry("680x680")

frame = LabelFrame(root, text="Ping now!", padx=50, pady=50, bg="light blue")
# the pack pad goes outside the frame
frame.pack(padx=10, pady=10)

frame2 = LabelFrame(root, padx=10, pady=10, bg="red")
# the pack pad goes outside the frame
frame2.pack()


frame3 = LabelFrame(root, text="Result Section", padx=10, pady=10, bg="lightblue")
# the pack pad goes outside the frame
frame3.pack()

website_name = Entry(frame)
website_name.pack()

#######################################################################################################################
#######################################################################################################################


def result_output():
    try:
        the_ping = PingTool(website_name.get())
        the_ping.ping()
        temp_list = the_ping.ping()
        packet_delay_1 = "sample delay for one packet= " + str(int(temp_list[0])) + "ms"
        total_delay = 0
        for x in temp_list:
            total_delay += x

        # -1 because last element in list is the packet loss percentage
        average_packet_delay_value = int(total_delay) / (len(temp_list) - 1)

        average_packet_RTT_delay = "Average time delay for all packets  = " + str(average_packet_delay_value) + "ms"
        packet_loss_result = "packet loss= " + str(temp_list[-1]) + "%"

        end_of_ping = "--------------------------------------"
        Label(frame3, text=packet_delay_1).pack()
        Label(frame3, text=average_packet_RTT_delay).pack()
        Label(frame3, text=packet_loss_result).pack()
        Label(frame3, text=end_of_ping).pack()
    except Exception as e:

        if \
                website_name.get()[-4:] != ".com" and website_name.get()[-7:] != ".edu.lb" \
                and website_name.get()[-4:] != ".org" and website_name.get()[-4:] != ".net" \
                and website_name.get()[-4:] != ".org" and website_name.get()[-4:] != ".int" \
                and website_name.get()[-4:] != ".gov" and website_name.get()[-7:] != ".edu" \
                and website_name.get()[-4:] != ".mil":
            Label(frame3, text="Invalid input URL").pack()
            Label(frame3, text="--------------------------------------").pack()

        else:
            Label(frame3, text="Server does not exist").pack()
            Label(frame3, text="--------------------------------------").pack()


result_btn = Button(frame, text="Click here to get results!", command=result_output, fg="blue")
result_btn.pack()
#######################################################################################################################
#######################################################################################################################
# Reference for update function and frame animation: GregFromBelbored.
# https://stackoverflow.com/questions/28518072/play-animations-in-gif-with-tkinter
# GIF reference : https://tenor.com/search/ping-pong-gifs
frameCnt = 12
frames = [PhotoImage(file='gif1.gif', format='gif -index %i' % i) for i in range(frameCnt)]


def update(ind):
    frame = frames[ind]
    ind += 1
    if ind == frameCnt:
        ind = 0
    gif_label.configure(image=frame)
    root.after(100, update, ind)


gif_label = Label(root)
gif_label.pack()
root.after(0, update, 0)
#######################################################################################################################
#######################################################################################################################
quit_button = Button(frame2, text="Exit", command=root.quit, fg="red")
quit_button.pack()
#######################################################################################################################
#######################################################################################################################
# Play music
# reference: https://www.youtube.com/watch?v=lQdWjesfSEk
pygame.mixer.init()

def play_music():
    pygame.mixer.music.load("The Chainsmokers Paris (Official Instrumental).mp3")
    pygame.mixer.music.play()


play_music()
#######################################################################################################################
#######################################################################################################################
root.configure(bg="lightblue")

#######################################################################################################################
#######################################################################################################################
root.mainloop()
#######################################################################################################################
#######################################################################################################################
'''
    GUI done by Jawad Srour
'''
