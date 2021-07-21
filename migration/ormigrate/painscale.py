

class PainScale(object):
    '''
    painscale handling
    '''

    @staticmethod
    def lookupPainImage(rating: int):
        '''
        Returns html image tag to the corresponding pain rating
       
        Args:
            rating(int): the pain rating
        '''
        painImages = {1: "http://rq.bitplan.com/images/rq/a/a3/Pain0.png",
                      2: "https://rq.bitplan.com/images/rq/0/01/Pain1.png",
                      3: "https://rq.bitplan.com/images/rq/0/0a/Pain4.png",
                      4: "https://rq.bitplan.com/images/rq/b/b0/Pain6.png",
                      5: "https://rq.bitplan.com/images/rq/6/6c/Pain7.png",
                      6: "https://rq.bitplan.com/images/rq/2/29/Pain10.png"
                      }
        if rating > 0 and rating < 7:
            return f'<img alt="{rating}" src="{painImages[rating]}" width="32" height="32"/>'
        else:
            return ""