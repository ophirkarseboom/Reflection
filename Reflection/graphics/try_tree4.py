# This example is provided with no promises or warranties regarding accuracy or suitability for any purpose whatsoever.

""" -- DragandDrop.pyw --
    A sample program demonstrating a Drag and Drop implementation within a wxTreeCtrl.
    The wxTreeCrtl shows two types of nodes, Series nodes and Collection nodes.
    This implementation allows users to drag Series nodes onto Collection nodes and
    Collection nodes onto Series nodes, but it blocks dragging nodes onto the same types.
    In my application, dragging certain types of nodes onto other types of nodes is
    often a meaningful action.  It does not always change the tree structure, but it
    often causes the copying or movement of data behind the scenes.  """


__author__ = 'David K. Woods, Ph.D., Wisconsin Center for Education Research, University of Wisconsin, Madison, dwoods at wcer dot wisc dot edu'

# Import wxPython
import wx
# use the fast cPickle tool instead of the regular Pickle
import pickle


# Declare the class for the main application Dialog Window
class MainWindow(wx.Dialog):
   """ This window displays a Tree Control that processes drag-and-drop activities. """
   def __init__(self,parent,id,title):
      # Create a Dialog Box
      wx.Dialog.__init__(self,parent,-1, title, size = (320,600), style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
      # Make the Dialog box white
      self.SetBackgroundColour(wx.WHITE)

      # Add a wxTreeCtrl to the Dialog box.  Use Layout Constraints to position it in the Dialog.
      lay = wx.LayoutConstraints()
      lay.top.SameAs(self, wx.Top, 10)         # Top margin of 10
      lay.bottom.SameAs(self, wx.Bottom, 30)   # Bottom margin of 30, to leave room for a button
      lay.left.SameAs(self, wx.Left, 10)       # Left margin of 10
      lay.right.SameAs(self, wx.Right, 10)     # Right margin of 10
      self.tree = wx.TreeCtrl(self, -1, style=wx.TR_HAS_BUTTONS)
      self.tree.SetConstraints(lay)

      # Add a wxButton to the Dialog box.  Use Layout Constraints to position it in the Dialog.
      lay = wx.LayoutConstraints()
      lay.top.SameAs(self, wx.Bottom, -25)     # Position the button at the bottom of the Dialog.
      lay.centreX.SameAs(self, wx.CentreX)     # Center the button horizontally
      lay.height.AsIs()
      lay.width.AsIs()
      btn = wx.Button(self, wx.ID_OK, "OK")
      btn.SetConstraints(lay)

      # Add a root node to the wxTreeCtrl.
      self.treeroot = self.tree.AddRoot('Transana Database')

      # Add a Series Root and three subnodes
      self.seriesroot = self.tree.AppendItem(self.treeroot, 'Series')
      item = self.tree.AppendItem(self.seriesroot, 'Series 1')
      item = self.tree.AppendItem(self.seriesroot, 'Series 2')
      item = self.tree.AppendItem(self.seriesroot, 'Series 3')

      # Add a Collection Root and three subnodes
      self.collectionsroot = self.tree.AppendItem(self.treeroot, 'Collections')
      item = self.tree.AppendItem(self.collectionsroot, 'Collection 1')
      item = self.tree.AppendItem(self.collectionsroot, 'Collection 2')
      item = self.tree.AppendItem(self.collectionsroot, 'Collection 3')

      # Expand the nodes so everything is visible initially
      self.tree.Expand(self.treeroot)
      self.tree.Expand(self.seriesroot)
      self.tree.Expand(self.collectionsroot)

      # Define the Begin Drag Event for the tree
      #wx.EVT_TREE_BEGIN_DRAG(self.tree, self.tree.GetId(), self.OnBeginDrag)
      self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)

      # Define the Drop Target for the tree.  The custom drop target object
      # accepts the tree as a parameter so it can query it about where the
      # drop is supposed to be occurring to see if it will allow the drop.
      dt = DropTarget(self.tree)
      self.tree.SetDropTarget(dt)

      # Lay out the screen and maintain the present layout
      self.Layout()
      self.SetAutoLayout(True)

      # Show the Dialog modally
      self.ShowModal()
      # Destroy the Dialog when we are done with it
      self.Destroy()


   def OnBeginDrag(self, event):
      """ Left Mouse Button initiates "Drag" for Tree Nodes """
      # Items in the tree are not automatically selected with a left click.
      # We must select the item that is initially clicked manually!!
      # We do this by looking at the screen point clicked and applying the tree's
      # HitTest method to determine the current item, then actually selecting the item
      sel_item, flags = self.tree.HitTest(event.GetPoint())
      self.tree.SelectItem(sel_item)

      # Determine what Item is being "dragged", and grab it's data
      tempStr = "%s" % (self.tree.GetItemText(sel_item))
      print ("A node called %s is being dragged" % (tempStr))

      # Create a custom Data Object for Drag and Drop
      ddd = DragDropData()
      # In this case, the data is trivial, but this could easily be a more complex object.
      ddd.SetSource(tempStr)

      # Use cPickle to convert the data object into a string representation
      pddd = pickle.dumps(ddd, 1)

      # Now create a wxCustomDataObject for dragging and dropping and
      # assign it a custom Data Format
      cdo = wx.CustomDataObject(wx.DataFormat('TransanaData'))
      # Put the pickled data object in the wxCustomDataObject
      cdo.SetData(pddd)

      # Sorry, I am not able to figure out how to extract data from a wxDataObjectComposite until after
      # it's been dropped, so I'm ignoring that aspect of things for now.  I've left the code commented
      # out for others who wish to pursue it.

      # Now put the CustomDataObject into a DataObjectComposite
#      tdo = wx.DataObjectComposite()
#      tdo.Add(cdo)

      # Create a Custom DropSource Object.  The custom drop source object
      # accepts the tree as a parameter so it can query it about where the
      # drop is supposed to be occurring to see if it will allow the drop.
      tds = DropSource(self.tree)
      # Associate the Data with the Drop Source Object
      # I've associated both the pickled CustomDataObject and the raw data object here
      # so that I can easily work with the data being dragged.  I'm sure this is poor
      # form and unnecessary, but there it is.  You don't like it, you are welcome to fix it!
      print(cdo, ddd)
      tds.SetData(cdo, ddd)    # (tdo) would be used in place of (cdo) if I were using the DataObjectComposite object

      # Initiate the Drag Operation
      dragResult = tds.DoDragDrop(True)

      # Report the result of the final drop when everything else is completed by the other objects
      if dragResult == wx.DragCopy:
          print ("Result indicated successful copy")
      elif dragResult == wx.DragMove:
          print ("Result indicated successful move")
      else:
          print ("Result indicated failed drop")
      print


class DropSource(wx.DropSource):
   """ This is a custom DropSource object designed to provide feedback to the user during the drag """
   def __init__(self, tree):
      # Create a Standard wxDropSource Object
      #wx.DropSource.__init__(self)
      # Remember the control that initiate the Drag for later use
      self.tree = tree

   # SetData accepts an object (obj) that has been prepared for the DropSource SetData() method
   # and a copy of the original data for internal use.  I suppose I should rewrite this to
   # just accept the original data and do the wxDataObject packaging here.  Maybe when I have time.
   def SetData(self, obj, originalData):
      # Set the prepared object as the wxDropSource Data
      wx.DropSource.SetData(self, obj)
      # hold onto the original data for later use
      self.data = originalData

   # I want to provide the user with feedback about whether their drop will work or not.
   def GiveFeedback(self, effect):
      # This method does not provide the x, y coordinates of the mouse within the control, so we
      # have to figure that out the hard way. (Contrast with DropTarget's OnDrop and OnDragOver methods)
      # Get the Mouse Position on the Screen
      (windowx, windowy) = wx.GetMousePosition()
      # Translate the Mouse's Screen Position to the Mouse's Control Position
      (x, y) = self.tree.ScreenToClientXY(windowx, windowy)
      # Now use the tree's HitTest method to find out about the potential drop target for the current mouse position
      (id, flag) = self.tree.HitTest((x, y))
      # I'm using GetItemText() here, but could just as easily use GetPyData()
      tempStr = self.tree.GetItemText(id)

      # This line compares the data being dragged (self.data) to the potential drop site given by the current
      # mouse position (tempStr).  If we are going (from Series to Collection) or (from Collection to Series),
      # we return FALSE to indicate that we should use the default drag-and-drop feedback, which will indicate
      # that the drop is legal.  If not, we return TRUE to indicate we are using our own feedback, which is
      # implemented by changing the cursor to a "No_Entry" cursor to indicate the drop is not allowed.
      # Note that this code here does not prevent the drop.  That has to be implemented in the Drop Target
      # object.  It just provides visual feedback to the user.
      if self.data.SourceText.startswith('Series') and tempStr.startswith('Collection') or \
         self.data.SourceText.startswith('Collection') and tempStr.startswith('Series'):
         # FALSE indicates that feedback is NOT being overridden, and thus that the drop is GOOD!
         return wx.false
      else:
         # Set the cursor to give visual feedback that the drop will fail.
         self.tree.SetCursor(wx.StockCursor(wx.CURSOR_NO_ENTRY))
         # Setting the Effect to wxDragNone has absolutely no effect on the drop, if I understand this correctly.
         effect = wx.DragNone
         # returning TRUE indicates that the default feedback IS being overridden, thus that the drop is BAD!
         return True



class DragDropData(object):
   """ This is a custom DragDropData object.  It's pretty minimalist, but could be much more complex if you wanted. """
   def __init__(self):
      self.SourceText = ''

   def __repr__(self):
      return "SourceText = '%s'" % (self.SourceText)

   def SetSource(self, txt):
      self.SourceText = txt



class DropTarget(wx.DropTarget):
   """ This is a custom DropTarget object designed to match drop behavior to the feedback given by the custom
       Drag Object's GiveFeedback() method. """
   def __init__(self, tree):
      # use a normal wxDropTarget
      wx.DropTarget.__init__(self)
      # Remember the source Tree Control for later use
      self.tree = tree

      # specify the data formats to accept
      self.df = wx.DataFormat('TransanaData')
      # Specify the data object to accept data for this format
      self.cdo = wx.CustomDataObject(self.df)
      # Set the DataObject for the DropTarget
      self.SetDataObject(self.cdo)

   def OnEnter(self, x, y, d):
      # print "OnEnter %s, %s, %s" % (x, y, d)
      # Just allow the normal wxDragResult (d) to pass through here
      return d

   def OnLeave(self):
      # print "OnLeave"
      pass

   def OnDrop(self, x, y):
      # Process the "Drop" event
      # print "Drop:  x=%s, y=%s" % (x, y)
      # Use the tree's HitTest method to find out about the potential drop target for the current mouse position
      (id, flag) = self.tree.HitTest((x, y))
      # I'm using GetItemText() here, but could just as easily use GetPyData()
      tempStr = self.tree.GetItemText(id)
      # Remember the Drop Location for later Processing (in OnData())
      self.DropLocation = tempStr
      print ("Dropped on %s." % tempStr)
      # Because the DropSource GiveFeedback Method can change the cursor, I find that I
      # need to reset it to "normal" here or it can get stuck as a "No_Entry" cursor if
      # a Drop is abandoned.
      self.tree.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
      # We don't yet have enough information to veto the drop, so return TRUE to indicate
      # that we should proceed to the OnData method
      return True

   # You can't know about the Source Data's characteristics in the OnDragOver method, so instead of
   # doing any processing here to determine if a drop is legal or not, we use the DropSource's OnFeedback
   # method and the DropTarget's OnData method to implement feedback and to allow or veto the drop
   # respectively
   # def OnDragOver(self, x, y, d):
   #    print "OnDragOver %s, %s, %s" % (x, y, d)
   #    I used to have a bunch of other logic here, but it could only know drop target information,
   #    and I needed to know about the Source of the Drag as well.

   def OnData(self, x, y, d):
      # once OnDrop returns TRUE, this method is automatically called.
      # print "OnData %s, %s, %s" % (x, y, d)
      # Let's get the data being dropped so we can do some processing logic
      if self.GetData():
         data = pickle.loads(self.cdo.GetData())
         print ("Drop Data = '%s' dropped onto %s" % (data, self.DropLocation))

      # This line compares the data being dragged (data) to the potential drop site determined in OnDrop and
      # passed here as self.DropLocation.  If we are going (from Series to Collection) or (from Collection to Series),
      # we do nothing to veto the drop because the drop is legal.  If not, we veto the drop by changing the wxDragResult
      # variable to indicate the drop is not allowed.
      # Note that this code here implements the drop logic and needs to match the logic in the DropSource's GiveFeedback()
      # method.  I should probably write a common function that both objects use to determine how to act.
      if data.SourceText.startswith('Series') and self.DropLocation.startswith('Collection') or \
         data.SourceText.startswith('Collection') and self.DropLocation.startswith('Series'):
         # If we meet the criteria, we do nothing to interfere with the drop process
         pass
      else:
         # If the test fails, we prevent the drop process by altering the wxDropResult (d)
         d = wx.DragNone


      # We can implement the desired behavior resulting from the drag and drop here!
      # Note that this example intentionally does nothing more than give feedback via the print statement.
      # If you want to experiment with having drag and drop alter the tree, be my guest.
      if d == wx.DragCopy:
          print ("OnData Result indicated successful copy")
      elif d == wx.DragMove:
          print ("OnData Result indicated successful move")
      else:
          print ("OnData Result indicated failed drop")
      return d



class MyApp(wx.App):
   def OnInit(self):
      frame = MainWindow(None, -1, "Drag and Drop Test")
      self.SetTopWindow(frame)
      return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()