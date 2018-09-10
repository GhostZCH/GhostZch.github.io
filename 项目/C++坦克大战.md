## C++坦克大战

[www.zhaoch.top](http://www.zhaoch.top) > [项目](http://www.zhaoch.top/项目)

# c++写的坦克大战

代码:

https://github.com/GhostZCH/Tankwar

一个练习项目，详细介绍
https://www.cnblogs.com/GhostZCH/archive/2013/04/10/3012571.html


整体的思路将程序分成3层，四个大块，3层好理解就是MVC的三次了，除了这三层还需要一个基础数据模块，模块被三层公用，提供基础功能，类似物理引擎吧，不过功能小得多。

并没有使用一般桌面程序使用的事件驱动模式，而是使用了游戏中广泛应用的帧循环模式，程序启动时开始帧循环直到程序退出，用户操作不是被立即相应的，而是被记录下来等到下一个帧循环的时候处理。每一个帧循环首先处理用户操作更新物理数据信息，然后使用更新后的数据重绘界面。


整体设计如下，程序在设计基础上写的，最终可能有些不同：

![](https://images0.cnblogs.com/blog/320730/201304/10154736-f4ffd06fcd24430b8e3893aee0be28a6.jpg)

类比较多，分开看就容易了，首先从控制器开始。控制器的作用是连接数据模型和视图，将用户操作传给后台，同时将后台数据传给前台，通知前台显示。如果说视图类似一个饭店的餐厅，数据模型就是这个饭店的后厨，而控制器就像是一个大堂经理，餐厅里客人点菜吃菜，后厨忙着做菜，经理的任务就是告诉厨师需要在什么时候做什么菜，同时通知服务员将做好的菜端给点菜的客人，经理从不动手做饭也不亲自接待客人只是发号施令，服务员不进后厨，后厨也不进大堂。如果不分开，就是在饭店大堂里直接开火做饭，想必这样的馆子也只能是路边小摊。

为了让整个程序的数据模型和界面可以独立演化，设置了两个接口IView 和IModel，Controller中用到的也是这两个接口，这也符合面向接口编程而不是面向实现编程的原则，以后的Model和View们只需要实现这两个接口就可以了，两者互不相关，都可以独自的发展。

Controller中提供了两种不同的使用模式，一种是自启动循环，另一种是由外界驱动帧循环。

第一种程序如下，在类似命令行这种不存在循环的程序中可以直接启动一个循环：

    void Controller::Go()
    {
        // Initialization
        time_t last_time = clock();
    
        // run
        while(_state!=STATE_ESC)
        {
            // time
            time_t this_time = clock();
            int derta_time = this_time - last_time;
            last_time = this_time;
    
            //user operation
            USER_OPERATION op = _view->GetUserOperation();
            LoopOperation(op, derta_time);
        }
    }

在Main 函数启动后就启动循环了

    int _tmain(int argc, _TCHAR* argv[])
    {
        Controller *game = new Controller(new ConsoleView(),  new ModelA());
        game->Go();
        return 0;
    }
 

另一种情况是界面架构就已经在循环中（如MFC），或者界面架构可以启动循环如openGL,ORGE等，这时就使用外部循环驱动程序：

    bool Controller::TimerTick( int dertaTime )
    {
        USER_OPERATION op = _view->GetUserOperation();
        LoopOperation(op, dertaTime);

        if(_state!=STATE_ESC) return true;
        else return false;//用户选择退出
    }


MFC的启动如下：

    void CTankWarMFCDlg::OnTimer(UINT_PTR nIDEvent)

        if(!_gameController->TimerTick(TIMER_SPAN))
        this->OnCancel();
        __super::OnTimer(nIDEvent);
        
        _userOP = USER_NONE;
    }
 
整个Controller针对的都是接口IView和IModel,不依赖具体的实现，只要在初始化Controller实例的时侯传入View与Model的实例即可。Controller的构造函数如下：

Controller(IView *view, IModel *model);

初始化时传入不同的参数也就应用不同的视图和模型如：

Controller *game = new Controller(new ConsoleView(),new ModelA());//命令行界面和模型A

// this 在 CTankWarMFCDlg 中使的，该类实现了IView接口是MFC的窗口

_gameController = new Controller(this,new ModelB());//MFC界面和模型B

 

LoopOperation( USER_OPERATION op, int derta_time )是控制器中重要的函数，执行帧循环，参数是用户在两帧中的操作，derta_time 是两帧的间隔时间，通常是毫秒级的，函数首先处理系统操作，如果用户选择退出，将停止循环。接下来如果游戏处于进行状态，通知模型更新数据，最后在界面中显示模型中的数据。

    void Controller::LoopOperation( USER_OPERATION op, int derta_time )
    {
        HandleSysOperation(op);//handle sys op

        string *alert = NULL;
        if(_state==STATE_GO)
        {
            _model->FrameStart(derta_time,UserOpToTankOp(op));// frame go
            if (_model->IsLose()) alert = new string("GAME OVER!");
            if (_model->IsWin()) alert = new string("YOU WIN!");
            if (_model->IsLose()||_model->IsWin())    StartOrStop();
        }
        Information *information = _model->GetInformation();
        information->AlertMsg(alert);

        _view->DisplayInformation(information); // information
        _view->DisplayGrid(_model->GetGird()); // draw grid

        delete information;
    }
 

接口中完全是纯虚函数构成，代码如下：

    class IView
    {
    public:
        IView(void);
        ~IView(void);

        virtual void DisplayGrid(Grid* grid) = 0;
        virtual void DisplayInformation(Information* information) = 0;

        virtual USER_OPERATION GetUserOperation() = 0;

        virtual void Initialization() = 0;
        virtual void Clear() = 0;
    };

    class IModel
    {

    public:
        IModel(void);
        ~IModel(void);

        virtual Grid* GetGird() = 0;
        virtual Information* GetInformation()= 0;

        virtual void Initialization()= 0;
        virtual void Clear()= 0;

        virtual  bool IsWin()= 0;
        virtual  bool IsLose()= 0;

        virtual void FrameStart(int dertaTime, TANK_OPERATION op)= 0;
    };
    

控制器说完说下界面层，共开发了两个界面，事实上我的开发顺序是这样的，先开发了ModelA 为了测试ModelA开发了控制台界面，控制台测试通过后又开发了MFC的界面，为了MFC界面取得更好的游戏效果，在ModelA的基础上写了ModelB，可以看到两者很多代码都是一样的。这里有个小问题，看似这种复制粘贴的方法有违代码复用的原则，但是这里我更多的考虑可以在不影响已有部分的情况下进行改进，代码的独立性更为重要，这也说明一个问题，复用率不是越高越好，复用也要考虑合理性。

界面的详细代码就不贴了，只显示一下界面的定义：

    class CTankWarMFCDlg : public CDialog,public IView

    class ConsoleView :public IView

界面代码的内容是用各自的形式将数据展示出来，ConsoleView 里使用的多是一些cout，CTankWarMFCDlg 则使用了复杂一些的GDI与窗口的重绘。只贴两小段代码示意一下。

    void ConsoleView::DisplayGrid( Grid* grid )
    {
        if(!grid) return;

        int h  = grid->Height();
        int w = grid->Width();
        char *data = new char[h*w];

        for (int i=0;i<h*w;i++)
            data[i] = ' ';

        for(list<Bullet*>::const_iterator iter = grid->BulletList()->begin(); iter!=grid->BulletList()->end();iter++)
        { 
            int x = (*iter)->Position()->X();
            int y = (*iter)->Position()->Y();

            data[y*w+x] = '*';
        }

        if (grid->User())
        {
            int x = grid->User()->Position()->X();
            int y = grid->User()->Position()->Y();
            data[y*w+x] = 'A';
        }

        for(list<AITank*>::const_iterator iter = grid->AiTankList()->begin(); iter!=grid->AiTankList()->end();iter++)
        { 
            int x = (*iter)->Position()->X();
            int y = (*iter)->Position()->Y();

            data[y*w+x] = 'o';
        }

        cout<<"======================================================"<<endl;
        for (int i=0;i<h;i++)
        {
            cout<<"||";
            for (int j=0;j<w;j++)
            {
                printf("%c",data[i*w+j]);
            }
            cout<<"||"<<endl;
        }
        cout<<"======================================================"<<endl;
    }

MFC

    void CTankWarMFCDlg::DrawAiTank( CDC *pDc,float hStep,float wStep,list<AITank*> *tankList )
    {
        pDc->SelectObject(_aiTank);//选择画笔
        for(list<AITank*>::iterator iter = tankList->begin();iter!=tankList->end();iter++)
        {
            AITank *t = (*iter);
            Vect2d *pos = t->Position();
            float r = t->Radius();

            float x = pos->X();
            float y = pos->Y();

            int x1 = (x-r)*wStep;
            int x2 = (x+r)*wStep;
            int y1 = (y-r)*hStep;
            int y2 = (y+r)*hStep;

            pDc->Ellipse(x1,y1,x2,y2);
        }
    }

 

界面如下所示：

![](https://images0.cnblogs.com/blog/320730/201304/10160310-7ae0e76f1a67418f9e582eca853c1930.png)
![](https://images0.cnblogs.com/blog/320730/201304/10160336-e1c83c4d8b364c6cb59030b7c6a8b87f.png)
![](https://images0.cnblogs.com/blog/320730/201304/10160410-afd0deef182342ac9fee7ffdb0cf5a0e.png)


数据模型中，是两个实现IModel的类（每次启动只使用一个），用ModelB进行说明：h文件的定义如下：

    class ModelB:
        public IModel
    {
    public:
        const static int GIRD_HEIGHT = 250;
        const static int GIRD_WIDTH = 250;
        const static int TANK_RADIUS = 5;
        const static int WAVE_COUNT = 3;

    private:
        Grid *_grid;
        string *_msg;

        int _wave;
        int _score;
        long _totalTime;

    public:
        ModelB(void);
        ~ModelB(void);
    
        Grid* GetGird();
        Information* GetInformation();

        void Initialization();
        void Clear();

        bool IsWin();
        bool IsLose();

        void FrameStart( int dertaTime, TANK_OPERATION op );

    private:
        void NewWave();
        bool NeedNewWave();

        void UserOperation( int dertaTime,TANK_OPERATION op);
        void BulletsOperation(int dertaTime);
        void TanksOperation(int dertaTime);
    };
 

实现接口的公告方法是留给控制器调用的，内部方法是为了方便实现自己添加的，Model中最复杂的是void FrameStart( int dertaTime, TANK_OPERATION op );函数，它是每帧的操作，在游戏进行时每次帧循环都会被调用一次用来提示数据模型根据用户操作更新数据。


    void ModelB::FrameStart( int dertaTime, TANK_OPERATION op )
    {
        if (_grid)
        {
            _totalTime+=dertaTime;
            UserOperation(dertaTime,op);
            BulletsOperation(dertaTime);
            TanksOperation(dertaTime);

            if(NeedNewWave()) NewWave();
        }
    }
    

单独看这个函数比较清晰简单，但是他调用过的5个函数就比较复杂了，几乎占了Model代码量的多半，响应用户操作，坦克的移动，发射子弹，碰撞检测，子弹的击中事件，敌人的添加和减少。。。是游戏逻辑的实现。

贴上一个函数示意一下过程：

    void ModelB::TanksOperation( int dertaTime )
    {
        UserTank* user_tank = _grid->User();
        list<AITank *> *tanklist = _grid->AiTankList();
        list<AITank *>::iterator i,j;
    
        for (i = tanklist->begin();i!=tanklist->end();i++)
        {
            AITank *t = (*i);
            t->GetAIOperation();

            if (t->IsNeedMove())
            {
                Circle *c = t->GetNextPosition(dertaTime);

                //if inside grid
                if(!_grid->IsInside(c)) break;
    
                // if impact user tank break
                if (c->IsImpact(user_tank)) break;

                // if impact other AI tank break
                bool isImpact = false;
                for (j = tanklist->begin();j!=tanklist->end();j++)
                {
                    if(i!=j && c->IsImpact(*j)) 
                    {
                        isImpact = true;break;
                    }
                }
                if(!isImpact)//move
                    t->Operation(dertaTime);
            } 
            else
            {
                t->Operation(dertaTime);
            }

            Bullet *b = t->GetBullet();
            if(b) _grid->BulletList()->push_back(b);

            // 子弹太多就去掉最老的
            if (_grid->BulletList()->size()>50)
            {
                Bullet *b =*( _grid->BulletList()->begin());
                _grid->BulletList()->pop_front();
                delete b;
            }
        }
    }

需要移动的坦克先检查是否碰撞，不碰撞的向前移动，碰撞的停止，如果坦克的操作时开炮就要获得它的炮弹，获得炮弹使用的是工厂模式，后面再细细说来。

## 说完了这三部分就要谈谈本次开发最复杂的部分——基础数据

看似很复杂其实只要抓住主线就很简单了，最基础的类是Circle，代表一个圆，是碰撞基础元素，MoveCircle继承自Circle增加了速度和方向属性，MoveCircle分开两支为坦克和炮弹，坦克又分成用户可操作的坦克与电脑控制的敌军，两者的区别是在Aitank有一个Ai属性，这里用了一个策略模式，Aitank可以有不同类型的Ai（这次就只写了一种，但是支持更多）。其他的类都是辅助这根主线。

两个Factory类方便获取子弹和坦克，简化了Model的操作，也方便维护，以TankFactory为例说明一下：

头文件

    class TankFactory
    {
    private:
        TankFactory(void);
        ~TankFactory(void);

    public:
        static Tank *GetTank(TANK_TYPE type,Vect2d *pos,DIRCTION dir,float r=1);

    private:
        static UserTank *GetUserTank(Vect2d *pos,DIRCTION dir,float r=1);
        static AITank *GetStdAITank(Vect2d *pos,DIRCTION dir,float r=1);
    };

    Tank * TankFactory::GetTank( TANK_TYPE type,Vect2d *pos,DIRCTION dir,float r)
    {
        switch(type)
        {
        case TANK_USER: return GetUserTank(pos,dir,r);break;
        case TANK_AI_STD:return GetStdAITank(pos,dir,r);break;
        default:return NULL;
        }
    }

    UserTank * TankFactory::GetUserTank( Vect2d *pos,DIRCTION dir,float r)
    {
        return new UserTank(USER_TANK_TOP_HP,USER_TANK_TOP_HP,BULLET_STD_USER,pos,dir,USERTANK_SPEED,r);
    }

    AITank * TankFactory::GetStdAITank( Vect2d *pos,DIRCTION dir,float r)
    {
        return new AITank(new StandardAI(),AI_TANK_TOP_HP,AI_TANK_TOP_HP,BULLET_STD,pos,dir,AITANK_SPEED,r);
    }


使用：

    TankFactory::GetTank(TANK_AI_STD,new Vect2d(x,y),DIR_UP,TANK_RADIUS)

第一个参数是一个枚举

    enum TANK_TYPE
    {
        TANK_USER,
        TANK_AI_STD
    };
 

如果以后需要更多类型的坦克只需要添加枚举，添加坦克类，对Factory的switch家一项即可，不影响其他部分的代码。当然在我这个微小的系统中，工厂模式的效果可能并不明显，但如果在初始化实例时还有复杂的操作时，这个优势就很明显了。封装，减少耦合是提高代码稳定性的重要途径。

剩下的类就只有Gird了，这各类的意思是游戏区域，是一个逻辑概念，并不是用户在界面上看到的显示区域，显示区域可达可小，取决于View的设置，与底层逻辑无关。
## The End

+ My [github location](https://github.com/GhostZCH/)
+ View Source of this website [GhostZch.github.io](https://github.com/GhostZCH/GhostZch.github.io/)
+ Commit [issues](https://github.com/GhostZCH/GhostZch.github.io/issues) to discuss with me and others
