#! python $this

# Tree as Table:
#  setRoot() #set the root node
#  setData() # raise not implemented error
#  getData() # return the current list of data :: [ leaf.data for leaf in self.data ]
# enforce select mode of exactly one item at a time.
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# when collapsed a node will pretend to not have children.
# painter should generally ignore the width of the cell
# tab in by N * depth pixels.  N should be some integer like '4'
 
# to get an icon 
# QCoreApplication.instance().style().standardIcon(QStyle.SP_DialogSaveButton) 
# http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qstyle.html
# QStyle.SP_FileIcon
# QStyle.SP_DirIcon
 
 
class Leaf(object):
    column_token = "<internal-leaf-item>"
    
    fold_HAS_CHILDREN=0;
    fold_COLLAPSED=1;
    fold_SIBLINGB=4;
    fold_IS_EMPTY= 5;

    # children built from root will copy this value
    join_string = '.'
    sort_key = None # how to index a single item for sorting. defaults by text value

    def __init__(self,parent=None,text="",data=[],icon=None):
        self.tempid = 0
        self.data = data
        self.text = text
        self.fold = 0;
        self.__icon = None;
        self.setIcon(icon)
        self.parent=parent
        self.children = []
        self.collapsed = True;
        self.depth = 0;
        
        self.folder_empty = False
        
        self.sort_key = lambda x: x.text
        if self.parent != None:
            self.parent.children.append(self)
            self.join_string = self.parent.join_string
            self.sort_key = self.parent.sort_key
            self.__get_depth__()
        
        
    def __len__(self):
        try :
            return len(self.data)
        except:
            return 0
           
    def __getitem__(self,index):
        if isinstance(index,basestring):
            #this bit is a psudeo hack, to get around the 
            # implementation of a TableColumn,
            if index == Leaf.column_token :
                return self.text
        else:
            if index >= len(self):
                raise IndexError(" Index %s is out of bounds"%index)
       
        return self.data[index]
     
    def __in__(self):
        # a generator for each value in the leaf
        if self.data != None:
            for item in self.data:
                yield item
      
    def __contains__(self,item):
        if self.data == None:
            return False
        return item in self.data

    def __sort_key__(self,item):
        if item == None:
            return item
        return self.sort_key(item)
    
    def __getattr__(self,attr):
        # this makes the leaf nearly transparent...
        # accessing the leaf object is almost like accesing the data it contains.
        return self.data.__getattribute__(attr)
        
    def __str__(self):
        return str(self.text)
        
    def __unicode__(self):
        return unicode(self.text)
        
    def __unicoder__(self):
        if self.parent != None:
            return self.parent.__unicoder__() + self.join_string + unicode(self.text)
        return unicode(self.text)
        
    def __repr__(self):
        # a leaves' identity is it's parents name plus it's own name
        
        name = unicode(self.text)
        if self.parent != None:
            name = self.parent.__unicoder__() + self.join_string + name
        #if quote:
        #    name = 
        return "\"%s\""%name
    
    def __get_depth__(self):
        depth = 0
        parent = self.parent
        while parent != None:
            parent = parent.parent
            if parent == self:
                raise RuntimeError("Circular reference detected")
            depth += 1
        self.depth = depth

    def setParent(self,parent):
        if self.parent != None:
            self.parent.children.remove(self)
        
        self.parent = parent
        
        if parent != None:
            self.parent.children.append(self)
        
        self.__get_depth__()
        
    @property
    def icon(self):
    
        instance = QCoreApplication.instance()
        if isinstance(self.__icon,QPixmap):
            return self.__icon
        if instance != None and self.__icon != None:
            return instance.style().standardIcon(self.__icon).pixmap(16,16)
        return None    
    
    def setIcon(self,icon):
        """
        icon as QImage,QPixmap, or style attribute, e.g.  QStyle.SP_FileIcon
        # QCoreApplication.instance().style().standardIcon(QStyle.SP_DialogSaveButton) 
        # http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qstyle.html
        """
        if isinstance(icon,QImage):
            self.__icon = QPixmap.fromImage(icon)
        else:
            self.__icon = icon # is pixmap or style flag
  
    def setEmptyFolder(self):
        """
            the icon next to this item in a tree will display 
            like any normal expanding folder, without the visual
            indicator (+/-) that it actually can be expanded
        """
        self.folder_empty = True
        
    def toList(self):
        # return a list of all items sorted alphabetically
        return list(self.toListg())
    
    def toListg(self):
        # # # # a generator that pulls each item in order
        # # # # while building the lists, for each item set the 'fold' flags
        # # # self.fold = 0;
        # # # if len(self.children) > 0:
        # # #     self.fold |= 1<<Leaf.fold_HAS_CHILDREN
        # # #     
        # # # if self.collapsed:    
        # # #     self.fold |= 1<<Leaf.fold_COLLAPSED
        # # #     
        # # # yield self
        # # # 
        # # # if not self.collapsed:
        # # #     last_child = None
        # # #     id = 1
        # # #     for child in sorted(self.children,key=self.__sort_key__):
        # # #         if last_child != None:
        # # #             last_child.fold |= 1<<Leaf.fold_SIBLINGB
        # # #         last_item = None
        # # #         child.tempid = id
        # # #         yield child
        # # #         for item in child.toList()[1:]: # to list yeilds itself, i dont want that
        # # #             if last_item != None:
        # # #                 last_item.fold |= 1<<Leaf.fold_SIBLINGB
        # # #             last_item = item    
        # # #             yield item;
        # # #         id += 1
        # # #         last_child = child
        # # #     
        self.fold = 0
        if len(self.children) > 0:
            self.fold |= 1<<Leaf.fold_HAS_CHILDREN
        
        yield self
        
        if self.collapsed:       
           self.fold |= 1<<Leaf.fold_COLLAPSED
        else:
            children = sorted(self.children,key=self.__sort_key__)
            for child in children:
                
                for item in child.toList():
                    yield item
                child.fold |= 1<<Leaf.fold_SIBLINGB
            if len(children) > 0:
                children[-1].fold &= ~(1<<Leaf.fold_SIBLINGB)
       
    def collapse_all(self):
        self.collapsed = True
       
    def getChild(self,text,default_data=[]):
        # get the first child with 'text' as it's value for the text attribute
        # if it does not exist it will be created with default_data as the default data.
        # and with self as it's parent and the given value of text for it's text attribute
        text = unicode(text)
        for child in self.children:
            if text == child.text:
                return child
        
        return Leaf(self,text,default_data)
        
    @staticmethod 
    def items_to_tree(level_index,leaf_name,list_of_items):
        """
            level_index   as a list of indices into a single item.
            leaf_name     as a function that takes one object and returns the name of the object
            list_of_items as a list of items, of any type, as long as they support indexing
            
            The name for each level is the same as the string representation of
            the value contained at that index
            
            items will be placed into the last level
            
            e.g.
            Leaf.items_to_tree( [0,1], leaf_name=lambda x : x[2], items )
                turns items that contain 3 indexes into a tree sorted by the first, then second index
                finally leaf-nodes of the tree contain the items themselves wiht a tag given by the third index
            # conceivable i can now do:
            #  Leaf.items_to_tree([MpMusic.ARTIST,MpMusic.ALBUM],lambda x : x[MpMusic.TITLE], list_of_songs)
            
            
        """
        
        root = Leaf(None,"root",None)
        
        for item in list_of_items:
            pleaf = root
            for i in range(len(level_index)):
                pleaf = pleaf.getChild(item[level_index[i]],None)
            Leaf(pleaf,unicode(leaf_name(item)),item)
        return root    

        
if __name__ == '__main__':        
    items = [ ("art","abm1","ttl1"), ("art","abm1","ttl2"), ("art","abm2","ttl3"), ("art2","abm3","ttl4") ]     
    leaf = Leaf.items_to_tree([0,1],lambda x : x[2], items)
    leaves = leaf.toList()
    print leaves
    print [ leaf.data for leaf in leaves ] 
    print len(leaves)

# 3 albums with 12 songs per 100 artists = 100*3*12 = 3600 songs
# nlogn = 3600*log2(3600) ~3600*12   :: 43200
# 100*log100 + 3log3 + 12log12 ~ 100*6.6 + 100( 3*1.6 + 3( 12*3.6 ) )= 660 + 100*(134.4) = 13506



