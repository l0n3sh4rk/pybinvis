import os
import sys
import Tkinter 
from PIL import Image, ImageTk

COLOR_INT_DELTA = 0x40



IMAGE_SCALE = 2
BYTE_FREQUENCY_PLOT_HEIGHT = 100
IMAGE_WIDTH = 256 * IMAGE_SCALE
IMAGE_HEIGHT = 256 * IMAGE_SCALE

DELTA = 50
WINDOW_WIDTH = IMAGE_WIDTH + DELTA
WINDOW_HEIGHT = IMAGE_HEIGHT + BYTE_FREQUENCY_PLOT_HEIGHT + DELTA


DEFAULT_DATA_SIZE = 0x1000

SLIDER_SCALE = 100

def read_file(path):
    fd = open(path)
    data = fd.read()
    fd.close()
    return data


        
def create_image(data):
    
    def update_color(color_value):
        color_value += COLOR_INT_DELTA
        if color_value > 255:
            color_value = 255
        return color_value

    data_len = len(data)
    
    image = Image.new( 'RGB', (IMAGE_WIDTH, IMAGE_HEIGHT + BYTE_FREQUENCY_PLOT_HEIGHT), "black") 
    pixels = image.load() 

    byte_frequency = [0]*256
    
    for i in xrange(data_len-1):
        # This is for normal scale
        
        # x,y = data[i:i+2]
        # red, green, blue = pixels[x,y]

        # green = update_color(green)
        # blue = update_color(blue)
        
        # pixels[x,y] = (red, green, blue)


        # This is for N scale

        startx = data[i]*2
        starty = data[i+1]*2

        
        
        for dx in range(0, IMAGE_SCALE):
            for dy in range(0, IMAGE_SCALE):
                x = startx + dx
                y = starty + dy
                red, green, blue = pixels[x,y]
                green = update_color(green)
                blue = update_color(blue)
                pixels[x,y] = (red, green, blue)


        byte_frequency[data[i]] += 1
        
    # Fix off by one
    byte_frequency[data[i+1]] += 1

    # Draw byte frequency plot
    def normalize_frequency(f):
        return float(f) / data_len * 100


    f_max = normalize_frequency(max(byte_frequency))
    
    def scale_frequency(f):
        return f * BYTE_FREQUENCY_PLOT_HEIGHT / f_max
    
    
    end_y = IMAGE_HEIGHT + BYTE_FREQUENCY_PLOT_HEIGHT
    
    for i in range(256):

        f = normalize_frequency(byte_frequency[i])        
        f_scaled = scale_frequency(f)
        
        y = end_y - f_scaled - 1
        
        
        for j in range(IMAGE_SCALE):
            #print i+j, y
            x = i*2+j
            color = (0, 255 , 0)

            for k in range(int(y), end_y):
                #print x, k
                pixels[x, k] = color

    # Display uniform distribution as red line
    y_of_rand = end_y - scale_frequency(0.4) - 1
    
    for i in range(256 * IMAGE_SCALE):
        pixels[i, y_of_rand] = (255, 0, 0)
        
        
    return image



class BinaryViewer(Tkinter.Frame):

    def __init__(self, root, data):

        Tkinter.Frame.__init__(self, root, background="white")
        self.grid(row=0, column=0)

        self.root = root
        self.data = bytearray(data)
        self.data_size = len(data)

        self.data_offset = 0
        self.display_window_size = DEFAULT_DATA_SIZE

        #print float(self.data_size)/self.display_window_size/100
        
        self.scrolling_step = float(self.data_size)/self.display_window_size/100
        self.scrolling_step = float(self.data_size) / (SLIDER_SCALE+1)
        self.image = None
        self.tkimage = None
        self.label = None


        self.offset_label = Tkinter.Label(self.root, text = 0)
        self.offset_label.grid(row=0, column=0, columnspan=2)
        
        
        #var_ = Tkinter.IntVar()
        slide = Tkinter.Scale(root, command = self.on_slide_move,
                              length = IMAGE_HEIGHT, showvalue=0)
        slide.grid(row=1, column=0, sticky=Tkinter.N)


        self.update_image()
        self.label = Tkinter.Label(self.root, image=self.tkimage)
        self.label.grid(row=1, column=1)#.pack()

        #self.label.image = tkimage
        

    def update_image(self):

        if self.image:
            del self.image
            self.image = None
            
        start_ = self.data_offset
        end_ = self.data_offset + self.display_window_size
        data_chunk = self.data[start_:end_]
        self.image = create_image(data_chunk)

        
        if self.tkimage:
            del self.tkimage
            
        self.tkimage = ImageTk.PhotoImage(self.image)
        
        
        
    def render_image(self):
        self.update_image()
        self.label.configure(image = self.tkimage)
        self.label.image = self.tkimage


        
    def on_slide_move(self, offset):
        n = int(offset)
        #if n >= 100:
        #    n = 99
            
        self.data_offset = int(self.scrolling_step * n)# * self.display_window_size
        self.render_image()


        label_text = '%.8X -- %.8X' % (self.data_offset, self.data_offset+self.display_window_size)
        self.offset_label.configure(text = label_text)
        
        #print self.data_offset, self.data_size
        #print int(self.scrolling_step*int(offset))
        #print offset, self.data_offset
        
def main():
    if len(sys.argv)!=2:
        print 'Usage: %s <file>'%sys.argv[0]
        sys.exit()


    data = read_file(sys.argv[1])


    root = Tkinter.Tk()  
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - WINDOW_WIDTH)/2
    y = (screen_height - WINDOW_HEIGHT)/2
    root.geometry('%dx%d+%d+%d' % (WINDOW_WIDTH, WINDOW_HEIGHT, x, y))
    root.title("%s - Binary Viewer" % (os.path.basename(sys.argv[1])))

    app = BinaryViewer(root, bytearray(data))
    
    root.attributes('-topmost', True)
    root.mainloop()

if __name__ == '__main__':
    main()
