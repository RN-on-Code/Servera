class MyBody:
 
 def my_brain(self,her_name):
        her_name = "She"
        return her_name

 def my_heart(self,her_name):
        her_name = "She"
        return her_name
 
 def tell_her(self,my_feelings = ""):
      
      if self.my_brain(her_name="") == self.my_heart(her_name=""):
             her_name = self.my_brain(her_name="")
             
             print("I'm in love with",her_name)

      else:
             print("Can I have your friend's no. please?")
             my_feelings += "Another She! "
             

this_story = MyBody()
this_story.tell_her()
 

